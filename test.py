# TODO: Make run with python, once I've reverted python3 to python

# Standard libraries
import unittest
import os

# Numpy libraries
import numpy as np
from numpy import linalg

# Pylogram libraries
import pylogram
import solve
from helpers import *

class TestBuiltins(unittest.TestCase):
    def test_1(self):
        d = defaultdict(int)
        d['a'] = 1
        # self.assertEqual( d , dict(a=1,c=0) )
        d['b'] = 0
        # self.assertEqual( d , dict(a=1,c=0) )

class TestMatrixSolve(unittest.TestCase):
    def test_invert(self):
        A = [ [1, 1], [2, 0] ]
        A_ = ( (1, 1), (2, 0) )
        b = [ 3, 4 ]
        x = [ 2, 1 ]
        self.assertTrue( all( linalg.solve(A,b)==x ) )
        self.assertTrue( all( linalg.solve(A_,b)==x ) )
        # TODO: Test with superfluous and unsolvable lines
        
    def test_var(self):
        x = pylogram.Var('fred')
        self.assertEqual(str(x.var()),'fred')
        
    def test_normalised_constraint(self):
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        self.assertEqual( solve.normalised_constraint_for( 2*a + 6*b , a.var() ), a + 3*b )
        self.assertEqual( solve.normalised_constraint_for( 6*b - 2*a , a.var() ), a - 3*b )

    def test_reduce_constraint_by_equ_at_var(self):
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        self.assertEqual( solve.reduce_constraint_by_equ_for_var( (2*a+b==0), (b==-1), b.var() ), (2*a==1) )
        # self.assertEqual( solve.reduce_constraint_by_equ_for_var( (b==-1), (a+b==0), a.var() ), (b==-1) )
        
    @unittest.expectedFailure
    def test_canonical(self):
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        c = pylogram.Var('c')
        variables_ab = (a+b).variables()
        variables_abc = (a+b+c).variables()
        self.assertEqual( solve.canonical_form( [ 2*a==1 ], variables_ab ), [ a==0.5 ] )
        self.assertEqual( solve.canonical_form( [ 2*a==1, 1*b==0 ], variables_ab ), [ a==0.5, b==0 ] )

class TestHelpers(unittest.TestCase):
    def test_nonzero_dict(self):
        d = nonzero_dict()
        self.assertEqual( len(d), 0 )
        d[5] = d[5] + 1
        self.assertEqual( len(d), 1 )
        d[5] = d[5] - 1
        self.assertEqual( len(d), 0 )
        d[4] += 1
        self.assertEqual( len(d), 1 )
        d[4] -= 1
        self.assertEqual( len(d), 0 )

class TestPylogram(unittest.TestCase):
    def test_undefined(self):
        undef = pylogram._Undefined()
        self.assertIs( undef, undef ) 
        self.assertIs( undef + 1, undef ) 
        self.assertIs( undef - 1, undef ) 
        self.assertIs( undef * 5, undef ) 
        self.assertIs( undef * -5, undef ) 
        self.assertIs( undef - undef, undef ) 
        self.assertEqual( undef * 0, 0 ) 
        self.assertEqual( 0 * undef, 0 ) 
        self.assertRaises( AttributeError, getattr, undef, '__div__' )

    def test_interface(self):
        system = pylogram.System()
        a = pylogram.Var()
        system.constrain( 3==a*2 )
        # self.assertEqual( system.evaluate(a), 1.5 )
        
    def test_arithmetic(self):
        system = pylogram.System()
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        # Check compiles
        a + 2  
        a * 2
        a * -1
        1 * a
        -1 * a
        a + b
        a - 1
        a - b
        1 - a
        -1 * b == 0 - (2 * a)
        a == 2 
        b == a * 2
        (a + b) * 2
        (a + b) / 2

    def test_null_evaluations(self):
        system = pylogram.System()
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        self.assertEqual( system.evaluate( 3) , 3 )
        self.assertEqual( system.evaluate( 3*a +2 -2*a -a ) , 2 )
        self.assertTrue( (a-a).is_null() )
        self.assertFalse( a.is_null() )
        self.assertTrue( pylogram.Expr(0).is_null() )
        self.assertRaises( pylogram.Contradiction, lambda:pylogram.Expr(4).is_null() )
        self.assertRaises( AssertionError, system.evaluate, pylogram.Equ(a,b) )
        self.assertTrue( pylogram.Equ( a, a ) )
        self.assertTrue( pylogram.Equ( a + b, b + a ) )
        self.assertTrue( a == a )
        self.assertTrue( a + b == b + a )
        self.assertEqual( a, a )
        self.assertEqual( a + b, b + a )

    def test_simple_evaluations(self):
        system = pylogram.System()
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        system.constrain( a== 2)
        system.constrain( b== 3)
        self.assertEqual( system.evaluate(pylogram.Expr(2)/2), 1 )
        self.assertEqual( system.evaluate(a/2), 1 )
        self.assertEqual( system.evaluate(1*2), 2 )
        with self.assertRaises( TypeError): 1/b
        with self.assertRaises( AssertionError): a/b # TODO: make both use same error type
        self.assertEqual( system.evaluate(a/2), 1 )
        self.assertEqual( system.evaluate(b*2), 6 )
        self.assertEqual( system.evaluate((a+b)*2), 10 )
        self.assertEqual( system.evaluate( a*5 + b/3 -2*(a+b) - (-0.1) ), 1.1 )
    
    def test_equ(self):
        system = pylogram.System()
        a = pylogram.Var()
        b = pylogram.Var()
        # self.assertEqual( a==b, b==a )
        self.assertNotEqual( a==a, a==b )
        self.assertEqual( a==a, pylogram.Expr(0)==0 )
        self.assertNotEqual( a==a, 0 )
    
    def test_solve(self):
        system = pylogram.System()
        a = pylogram.Var()
        b = pylogram.Var()
        system.constrain( a + b == 3)
        system.constrain( 2 * a + b == 5)
        self.assertTrue( system.solved() )
        self.assertEqual( system.evaluate(a), 2 )
        self.assertEqual( system.evaluate(b), 1 )

    def test_system(self):
    
        # Variables
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        
        system = pylogram.System()

        # Not necessary for real code, but test results expect this order
        # self.assertTrue( hash(a) < hash(b) )
        # self.assertTrue( list({ a:1, b:2 }.keys())[0] is a )
        # TODO: Check hash for actual variables, not Expr(variable)

        # Check we can apply constraints, including duplicates
        system.constrain_equals( b , a * 2 )
        system.constrain_equals( b , 2 * a )
        system.constrain_equals( -1 * b , 0 - (2 * a) )

        self.assertFalse( system.solved() )
        self.assertIsNone( system.evaluate(a), None )
        self.assertIsNone( system.evaluate(b), None )

        system.constrain_equals( a , 3 )

        # Check intermediates
        self.assertEqual( tuple(system.x()), (a,b) )
        self.assertEqual( system.b(), (0,0,0,3) )
        self.assertEqual( system.A(), ((-2,1),(-2,1),(2,-1),(1,0)) )
        # self.assertTrue( system.solved() )
        # 
        # # Check results
        # self.assertEqual( system.evaluate(a), 3 )
        # self.assertEqual( system.evaluate(b), 6 )
        # self.assertEqual( system.evaluate(2*b), 12 )
        
        a == 2 
        system.constrain( b == a * 2 )

if __name__ == '__main__':
    unittest.main()