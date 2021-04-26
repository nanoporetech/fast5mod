"""Entry point for fast5mod package."""
import argparse
import logging
import sys

from fast5mod import __version__
import fast5mod.programs


def _log_level():
    """Parser to set logging level and acquire software version/commit."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)

    modify_log_level = parser.add_mutually_exclusive_group()
    modify_log_level.add_argument(
        '--debug', action='store_const',
        dest='log_level', const=logging.DEBUG, default=logging.INFO,
        help='Verbose logging of debug information.')
    modify_log_level.add_argument(
        '--quiet', action='store_const',
        dest='log_level', const=logging.WARNING, default=logging.INFO,
        help='Minimal logging; warnings only).')

    return parser


def main():
    """Run main entry point."""
    pymajor, pyminor = sys.version_info[0:2]
    if (pymajor < 3) or (pyminor not in {5, 6, 7, 8}):
        raise RuntimeError(
            '`medaka` is unsupported on your version of python, '
            'please use python 3.5 or python 3.6.')

    parser = argparse.ArgumentParser(
        'fast5mod', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    methparser = parser.add_subparsers(
        title='subcommands', description='valid commands',
        help='additional help', dest='command')
    methparser.required = True

    parser.add_argument(
        '--version', action='version',
        version='%(prog)s {}'.format(__version__))

    hdf2samparser = methparser.add_parser(
        'guppy2sam', parents=[_log_level()],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help=(
            'Convert Guppy .fast5 files with methylation calls to .sam '
            'file, output to stdout.'))
    hdf2samparser.set_defaults(func=fast5mod.programs.hdf_to_sam)
    hdf2samparser.add_argument(
        'path',
        help='Input path for .fast5 files.')
    hdf2samparser.add_argument(
        '--reference',
        help=(
            '.fasta containing reference sequence(s). If not given output '
            'will be unaligned sam.'))
    hdf2samparser.add_argument(
        '--workers', type=int, default=16,
        help='Number of alignment threads.')
    hdf2samparser.add_argument(
        '--io_workers', type=int, default=4,
        help='Number of .fast5 reader processes.')
    hdf2samparser.add_argument(
        '--recursive', action='store_true',
        help='Search for .fast5s recursively.')

    methcallparser = methparser.add_parser(
        'call', parents=[_log_level()],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help='Call methylation from .bam file.')
    methcallparser.set_defaults(func=fast5mod.programs.call_methylation)
    methcallparser.add_argument(
        'bam',
        help='Input .bam file (via `medaka methylation guppy2sam`).')
    methcallparser.add_argument(
        'reference',
        help='.fasta containing reference sequence(s).')
    methcallparser.add_argument(
        'output',
        help='Output file name.')
    methcallparser.add_argument(
        '--regions', nargs='+',
        help='bam region to process ("chrom:start-end").')
    methcallparser.add_argument(
        '--meth', default='cpg',
        choices=list(fast5mod.programs.MOTIFS.keys()),
        help='methylation type.')
    methcallparser.add_argument(
        '--filter', type=int, nargs=2, default=(64, 128),
        metavar=('upper', 'lower'),
        help=(
            'Upper (lower) score boundary to call canonical (methylated) '
            'base. Scores are in the range [0, 256].'))

    args = parser.parse_args()
    logging.basicConfig(
        format='[%(asctime)s - %(name)s] %(message)s', datefmt='%H:%M:%S',
        level=logging.INFO)
    logger = logging.getLogger(__package__)
    logger.setLevel(args.log_level)

    args.func(args)
