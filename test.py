# TODO: Make run with python, once I've reverted python3 to python

# Standard libraries
import unittest
import os

# Numpy libraries
import numpy as np
from numpy import linalg

# Pylogram libraries
import pylogram
from helpers import *

class TestMatrixSolve(unittest.TestCase):
    def test_invert(self):
        A = [ [1, 1], [2, 0] ]
        A_ = ( (1, 1), (2, 0) )
        b = [ 3, 4 ]
        x = [ 2, 1 ]
        self.assertTrue( all( linalg.solve(A,b)==x ) )
        self.assertTrue( all( linalg.solve(A_,b)==x ) )
        # TODO: Test with superfluous and unsolvable lines

class TestHelpers(unittest.TestCase):
    def test_nonzero_dict(self):
        d = nonzero_dict()
        self.assertEquals( len(d), 0 )
        d[5] = d[5] + 1
        self.assertEquals( len(d), 1 )
        d[5] = d[5] - 1
        self.assertEquals( len(d), 0 )
        d[4] += 1
        self.assertEquals( len(d), 1 )
        d[4] -= 1
        self.assertEquals( len(d), 0 )

class TestPylogram(unittest.TestCase):
    def test_undefined(self):
        undef = pylogram._Undefined()
        self.assertIs( undef, undef ) 
        self.assertIs( undef + 1, undef ) 
        self.assertIs( undef - 1, undef ) 
        self.assertIs( undef * 5, undef ) 
        self.assertIs( undef * -5, undef ) 
        self.assertIs( undef - undef, undef ) 
        self.assertEquals( undef * 0, 0 ) 
        self.assertEquals( 0 * undef, 0 ) 
        self.assertRaises( AttributeError, getattr, undef, '__div__' )

    def test_interface(self):
        system = pylogram.default_system()
        a = pylogram.Var()
        system.constrain( 3==a*2 )
        # self.assertEquals( system.evaluate(a), 1.5 )
        
    def test_arithmetic(self):
        system = pylogram.System()
        a = pylogram.Var()
        b = pylogram.Var()
        system.constrain( a== 2)
        system.constrain( b== 3)
        self.assertEquals( system.evaluate(pylogram.Expr(2)/2), 1 )
        self.assertEquals( system.evaluate(a/2), 1 )
        self.assertEquals( system.evaluate(1*2), 2 )
        with self.assertRaises( TypeError): 1/b
        # self.assertEquals( system.evaluate(a/2), 1 )
        # self.assertEquals( system.evaluate(b*2), 2 )
        
    def test_solve(self):
        system = pylogram.System()
        a = pylogram.Var()
        b = pylogram.Var()
        system.constrain( a + b == 3)
        system.constrain( 2 * a + b == 5)
        self.assertTrue( system.solved() )
        self.assertEquals( system.evaluate(a), 2 )
        self.assertEquals( system.evaluate(b), 1 )

    def test_system(self):
    
        # Variables
        a = pylogram.Var()
        b = pylogram.Var()
        
        system = pylogram.System()

        # Not necessary for real code, but test results expect this order
        # self.assertTrue( hash(a) < hash(b) )
        # self.assertTrue( list({ a:1, b:2 }.keys())[0] is a )
        # TODO: Check hash for actual variables, not Expr(variable)

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

        # Check null evaluations
        self.assertEquals( system.evaluate( 3) , 3 )
        self.assertEquals( system.evaluate( 3*a +2 -2*a -a ) , 2 )
        self.assertTrue( (a-a).is_null() )
        self.assertFalse( a.is_null() )
        self.assertTrue( pylogram.Expr(0).is_null() )
        self.assertRaises( pylogram.Contradiction, lambda:pylogram.Expr(4).is_null() )
        self.assertRaises( AssertionError, system.evaluate, pylogram.Equ(a,b) )
        self.assertTrue( pylogram.Equ( a, a ) )
        self.assertTrue( pylogram.Equ( a + b, b + a ) )
        # self.assertTrue( a == a )
        # self.assertTrue( a + b == b + a )
        # self.assertEquals( a, a )
        # self.assertEquals( a + b, b + a )

        # Check we can apply constraints, including duplicates
        system.constrain_equals( b , a * 2 )
        system.constrain_equals( b , 2 * a )
        system.constrain_equals( -1 * b , 0 - (2 * a) )

        self.assertFalse( system.solved() )
        self.assertIsNone( system.evaluate(a), None )
        self.assertIsNone( system.evaluate(b), None )

        system.constrain_equals( a , 3 )

        # Check intermediates
        self.assertEquals( system.x()[0], a )
        self.assertEquals( system.x()[1], b )
        self.assertEquals( system.b(), (0,0,0,3) )
        self.assertEquals( system.A(), ((-2,1),(-2,1),(2,-1),(1,0)) )
        # self.assertTrue( system.solved() )
        # 
        # # Check results
        # self.assertEquals( system.evaluate(a), 3 )
        # self.assertEquals( system.evaluate(b), 6 )
        # self.assertEquals( system.evaluate(2*b), 12 )
        
        a == 2 
        system.constrain( b == a * 2 )

if __name__ == '__main__':
    unittest.main(verbosity=2)