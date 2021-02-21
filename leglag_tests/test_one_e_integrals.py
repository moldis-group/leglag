"""
Tests that the one electron integrals for infinite domains are computed
correctly.
"""
import numpy as np
import pytest
from hypothesis import given, strategies as st
from scipy.special import gammainc

from leglag.one_d_domain import InfDomain
from leglag.one_e_integrals import inf_kinetic, inf_potential


@pytest.fixture(scope="module")
def unscaled_kinetic_matrix():
    """The unnormalised matrix of kinetic energy operator integrals for an
    infinite domain.

    This is currently limited to the first 5 indices.
    """
    matrix = np.zeros((5, 5))
    matrix[0, 0] = 2
    matrix[0, 1] = 2 / np.sqrt(3)
    matrix[1, 1] = 10 / 3
    matrix[0, 2] = np.sqrt(2 / 3)
    matrix[1, 2] = 5 * np.sqrt(2) / 3
    matrix[2, 2] = 14 / 3
    matrix[0, 3] = np.sqrt(2 / 5)
    matrix[1, 3] = np.sqrt(10 / 3)
    matrix[2, 3] = 14 / np.sqrt(15)
    matrix[3, 3] = 6
    matrix[0, 4] = 2 / np.sqrt(15)
    matrix[1, 4] = 2 * np.sqrt(5) / 3
    matrix[2, 4] = 14 * np.sqrt(10) / 15
    matrix[3, 4] = 2 * np.sqrt(6)
    matrix[4, 4] = 22 / 3
    matrix -= np.identity(5)
    # symmetrise the matrix
    matrix = matrix + matrix.T - np.diag(matrix.diagonal())
    return matrix


@pytest.fixture(scope="module")
def unscaled_potential_matrix_at_zero():
    """The unnormalised matrix of one electron potential energy operator
    integrals for an infinite domain.

    This is currently limited to the first 5 indices.

    Arguments:
        t: The position to evaluate the potential in space
    """
    matrix = np.zeros((5, 5))
    matrix[0, 0] = 0.5
    matrix[0, 1] = np.sqrt(3) / 6
    matrix[1, 1] = 0.5
    matrix[0, 2] = np.sqrt(6) / 12
    matrix[1, 2] = np.sqrt(2) / 4
    matrix[2, 2] = 0.5
    matrix[0, 3] = np.sqrt(10) / 20
    matrix[1, 3] = np.sqrt(30) / 20
    matrix[2, 3] = np.sqrt(15) / 10
    matrix[3, 3] = 0.5
    matrix[0, 4] = np.sqrt(15) / 30
    matrix[1, 4] = np.sqrt(5) / 10
    matrix[2, 4] = np.sqrt(10) / 10
    matrix[3, 4] = np.sqrt(6) / 6
    matrix[4, 4] = 0.5

    # symmetrise the matrix
    matrix = matrix + matrix.T - np.diag(matrix.diagonal())
    return matrix


@pytest.fixture(scope="module")
def unscaled_potential_matrix_at_one():
    """The unnormalised matrix of one electron potential energy operator
    integrals for an infinite domain.

    This is currently limited to the first 5 indices.

    Arguments:
        t: The position to evaluate the potential in space
    """
    matrix = np.zeros((5, 5))
    matrix[0, 0] = 0.22265723377644516939
    matrix[0, 1] = 0.065405800099614498450
    matrix[1, 1] = 0.18881028147037641162
    matrix[0, 2] = 0.025521944154822462867
    matrix[1, 2] = 0.073675506640146723778
    matrix[2, 2] = 0.16670864112832722749
    matrix[0, 3] = 0.011541995996367873672
    matrix[1, 3] = 0.033318872477442873513
    matrix[2, 3] = 0.075392002144926971448
    matrix[3, 3] = 0.15086251718467694008
    matrix[0, 4] = 0.0057391322761036405606
    matrix[1, 4] = 0.016567447822616532475
    matrix[2, 4] = 0.037487855047444645289
    matrix[3, 4] = 0.075014749779958562014
    matrix[4, 4] = 0.13879878682879274478

    # symmetrise the matrix
    matrix = matrix + matrix.T - np.diag(matrix.diagonal())
    return matrix


@given(
    functions=st.integers(min_value=1, max_value=50),
    side=st.booleans(),
)
def test_kinetic_matrix_shape(functions, side):
    """Tests that the shape of the kinetic energy integral matrix is correct."""
    domain = InfDomain(0, 0, side, 2, 1, functions, None)
    matrix = inf_kinetic(domain)
    assert matrix.shape == (
        functions,
        functions,
    )


@given(
    # This max value is the maximum range of the expected data type divided by
    # the largest element of the unscaled kinetic matrix, which prevents an
    # overflow error
    alpha=st.floats(min_value=0, max_value=2 * np.sqrt(np.finfo(np.float64).max) / 6),
    side=st.booleans(),
)
def test_kinetic_matrix_values(alpha, side, unscaled_kinetic_matrix):
    """Tests that the kinetic matrix is correctly generated by comparing to an
    analytically constructed example.
    """
    domain = InfDomain(0, 0, side, alpha, 1, min(unscaled_kinetic_matrix.shape), None)
    matrix = inf_kinetic(domain)
    assert np.isclose(
        matrix, alpha ** 2 * unscaled_kinetic_matrix / 2, atol=0, rtol=1e-14
    ).all()


@given(
    functions=st.integers(min_value=1, max_value=50),
    side=st.booleans(),
    nuclei=st.lists(st.tuples(st.floats(min_value=0), st.integers(min_value=1))),
)
def test_potential_matrix_shape(functions, side, nuclei):
    """Tests that the shape of the one electron potential energy integral
    matrix is correct.
    """
    domain = InfDomain(0, 0, side, 2, 1, functions, None)
    matrix = inf_potential(domain, 0)
    assert matrix.shape == (
        functions,
        functions,
    )


@given(
    alpha=st.floats(
        min_value=0, max_value=10 ** (np.log10(np.finfo(np.float64).max) / 2)
    ),
    side=st.booleans(),
    nuclei=st.lists(st.tuples(st.floats(min_value=0), st.integers(min_value=1))),
)
def test_potential_matrix_values_at_zero(
    alpha, side, nuclei, unscaled_potential_matrix_at_zero
):
    """Tests that the kinetic matrix is correctly generated by comparing to an
    analytically constructed example.
    """
    domain = InfDomain(
        0, 0, side, alpha, 1, min(unscaled_potential_matrix_at_zero.shape), None
    )
    matrix = inf_potential(domain, 0)
    assert np.isclose(
        matrix, 2 * alpha * unscaled_potential_matrix_at_zero, atol=0, rtol=1e-14
    ).all()


@pytest.mark.parametrize(
    "alpha,position,expected_matrix",
    [
        (
            2,
            1,
            np.array(
                [
                    [
                        0.60306079683378665927,
                        0.12784011696937552659,
                        0.037486952245518249652,
                        0.013108762856806335803,
                        0.0051495572630676102668,
                    ],
                    [
                        0.12784011696937552659,
                        0.51665968161851543467,
                        0.15150171379034025222,
                        0.052978434348840739448,
                        0.020811687904276340999,
                    ],
                    [
                        0.037486952245518249652,
                        0.15150171379034025222,
                        0.45911952506799888982,
                        0.16054890079162115197,
                        0.063068938478793636324,
                    ],
                    [
                        0.013108762856806335803,
                        0.052978434348840739448,
                        0.16054890079162115197,
                        0.41729904920753857386,
                        0.16392892092041569535,
                    ],
                    [
                        0.0051495572630676102668,
                        0.020811687904276340999,
                        0.063068938478793636324,
                        0.16392892092041569535,
                        0.38514368740123998198,
                    ],
                ]
            ),
        ),
        (
            0.7,
            3.5,
            np.array(
                [
                    [
                        0.18488870402209088733,
                        0.034999413128998148669,
                        0.0092834496726205206711,
                        0.0029640617151554127543,
                        0.0010707968626326696883,
                    ],
                    [
                        0.034999413128998148669,
                        0.15963467267289742612,
                        0.042342437123216826208,
                        0.013519284450203167054,
                        0.0048839763694181906751,
                    ],
                    [
                        0.0092834496726205206711,
                        0.042342437123216826208,
                        0.14252116220018659995,
                        0.045504799980003726799,
                        0.016439062926447980851,
                    ],
                    [
                        0.0029640617151554127543,
                        0.013519284450203167054,
                        0.045504799980003726799,
                        0.12994344770646939481,
                        0.046943366736365071840,
                    ],
                    [
                        0.0010707968626326696883,
                        0.0048839763694181906751,
                        0.016439062926447980851,
                        0.046943366736365071840,
                        0.12019739670863536310,
                    ],
                ]
            ),
        ),
    ],
)
def test_potential_matrix_values_at_one(alpha, position, expected_matrix):
    """Tests that the kinetic matrix is correctly generated by comparing to an
    analytically constructed example.
    """
    domain = InfDomain(0, 0, True, alpha, 1, min(expected_matrix.shape), None)
    matrix = inf_potential(domain, position)
    assert np.isclose(matrix, expected_matrix, atol=0, rtol=1e-14).all()
