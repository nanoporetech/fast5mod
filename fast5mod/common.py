"""Commonly used data structures and functions."""
import collections
import logging
import os

import pysam


# provide read only access to key region attrs
_Region = collections.namedtuple('Region', 'ref_name start end')


class Region(_Region):
    """Represents a genomic region."""

    @property
    def name(self):
        """Samtools-style region string, zero-base end exclusive."""
        return self.__str__()

    def __str__(self):
        """Return string representation of region."""
        # This will be zero-based, end exclusive
        start = 0 if self.start is None else self.start
        end = '' if self.end is None else self.end
        return '{}:{}-{}'.format(self.ref_name, start, end)

    @property
    def size(self):
        """Return size of region."""
        return self.end - self.start

    @classmethod
    def from_string(cls, region):
        """Parse region string into `Region` objects.

        :param region: region str

        >>> Region.from_string('Ecoli') == Region(
        ...     ref_name='Ecoli', start=None, end=None)
        True
        >>> Region.from_string('Ecoli:1000-2000') == Region(
        ...     ref_name='Ecoli', start=1000, end=2000)
        True
        >>> Region.from_string('Ecoli:1000') == Region(
        ...     ref_name='Ecoli', start=1000, end=None)
        True
        >>> Region.from_string('Ecoli:-1000') == Region(
        ...     ref_name='Ecoli', start=0, end=1000)
        True
        >>> Region.from_string('Ecoli:500-') == Region(
        ...     ref_name='Ecoli', start=500, end=None)
        True
        >>> Region.from_string('A:B:c:500-') == Region(
        ...     ref_name='A:B:c', start=500, end=None)
        True
        """
        if ':' not in region:
            ref_name, start, end = region, None, None
        else:
            start, end = None, None
            ref_name, bounds = region.rsplit(':', 1)
            if bounds[0] == '-':
                start = 0
                end = int(bounds.replace('-', ''))
            elif '-' not in bounds:
                start = int(bounds)
                end = None
            elif bounds[-1] == '-':
                start = int(bounds[:-1])
                end = None
            else:
                start, end = [int(b) for b in bounds.split('-')]
        return cls(ref_name, start, end)

    def split(region, size, overlap=0, fixed_size=True):
        """Split region into sub-regions of a given length.

        :param size: size of sub-regions.
        :param overlap: overlap between ends of sub-regions.
        :param fixed_size: ensure all sub-regions are equal in size. If `False`
            then the final chunk will be created as the smallest size to
            conform with `overlap`.

        :returns: a list of sub-regions.

        """
        regions = list()
        for start in range(region.start, region.end, size - overlap):
            end = min(start + size, region.end)
            regions.append(Region(region.ref_name, start, end))
        if len(regions) > 1:
            if fixed_size and regions[-1].size < size:
                del regions[-1]
                end = region.end
                start = end - size
                if start > regions[-1].start:
                    regions.append(Region(region.ref_name, start, end))
        return regions

    def overlaps(self, other):
        """Determine if a region overlaps another.

        :param other: a second Region to test overlap.

        :returns: True if regions overlap.

        """
        if self.ref_name != other.ref_name:
            return False

        def _limits(x):
            x0 = x.start if x.start is not None else -1
            x1 = x.end if x.end is not None else float('inf')
            return x0, x1

        a0, a1 = _limits(self)
        b0, b1 = _limits(other)
        return (
            (a0 < b1 and a1 > b0) or
            (b0 < a1 and b1 > a0))


def get_regions(bam, region_strs=None):
    """Create `Region` objects from a bam and region strings.

    :param bam: `.bam` file.
    :param region_strs: iterable of str in zero-based (samtools-like)
        region format e.g. ref:start-end or filepath containing a
        region string per line.

    :returns: list of `Region` objects.
    """
    with pysam.AlignmentFile(bam) as bam_fh:
        ref_lengths = dict(zip(bam_fh.references, bam_fh.lengths))
    if region_strs is not None:
        if os.path.isfile(region_strs[0]):
            with open(region_strs[0]) as fh:
                region_strs = [line.strip() for line in fh.readlines()]

        regions = []
        for r in (Region.from_string(x) for x in region_strs):
            start = r.start if r.start is not None else 0
            end = r.end if r.end is not None else ref_lengths[r.ref_name]
            regions.append(Region(r.ref_name, start, end))
    else:
        regions = [
            Region(ref_name, 0, end)
            for ref_name, end in ref_lengths.items()]

    return regions


def get_named_logger(name):
    """Create a logger with a name."""
    logger = logging.getLogger('{}.{}'.format(__package__, name))
    logger.name = name
    return logger


comp = {
    'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'X': 'X', 'N': 'N',
    'a': 't', 't': 'a', 'c': 'g', 'g': 'c', 'x': 'x', 'n': 'n',
    # '-': '-'
}
comp_trans = str.maketrans(''.join(comp.keys()), ''.join(comp.values()))


def reverse_complement(seq):
    """Reverse complement sequence.

    :param: input sequence string.

    :returns: reverse-complemented string.

    """
    return seq.translate(comp_trans)[::-1]
