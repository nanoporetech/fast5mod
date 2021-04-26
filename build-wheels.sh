#!/bin/bash
# Usage: ./build-wheels.sh <workdir> <pyminorversion1> <pyminorversion2> ...
set -e -x
export MANYLINUX=1

PACKAGE_NAME='fast5mod'

workdir=$1
shift

echo "Changing cwd to ${workdir}"
cd ${workdir}

yum install -y zlib-devel
make clean
mkdir -p wheelhouse

# Compile wheels
for minor in $@; do
    if [[ "${minor}" == "8" ]]  || [[ "${minor}" == "9" ]]; then
        PYBIN="/opt/python/cp3${minor}-cp3${minor}/bin"
    else
        PYBIN="/opt/python/cp3${minor}-cp3${minor}m/bin"
    fi
    # auditwheel/issues/102
    "${PYBIN}/pip" install --upgrade cffi setuptools pip wheel==0.31.1
    "${PYBIN}/pip" wheel . -w ./wheelhouse/
done


# Bundle external shared libraries into the wheels
for whl in "wheelhouse/${PACKAGE_NAME}"*.whl; do
    auditwheel repair "${whl}" -w ./wheelhouse/
done


# Install packages
for minor in $@; do
    if [[ "${minor}" == "8" || "${minor}" == "9" ]]; then
        PYBIN="/opt/python/cp3${minor}-cp3${minor}/bin"
    else
        PYBIN="/opt/python/cp3${minor}-cp3${minor}m/bin"
    fi
    "${PYBIN}/pip" install "${PACKAGE_NAME}" --no-index -f ./wheelhouse
done

cd wheelhouse && ls | grep -v "${PACKAGE_NAME}.*manylinux" | xargs rm
