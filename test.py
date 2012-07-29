# TODO: Make run with python, once I've reverted python3 to python

# Standard libraries
import unittest
import os
from fractions import Fraction

# Pylogram libraries
import pylogram
import solve
from solve import canonical
from helpers import *

class TestBuiltins(unittest.TestCase):
    def test_remove(self):
        class Foo:
            def __bool__(self, other):
                assert False
            def __eq__(self,other):
                return isinstance(other, Number) and other==4 or id(self)==id(other)
        fizz = Foo()
        buzz = Foo()
        l = [ 2, fizz, 4, buzz, fizz, 7 ]
        l.remove(buzz)
        self.assertEqual(l, [ 2, fizz, buzz, fizz, 7 ] )
        l.remove(buzz)
        self.assertEqual(l, [ 2, fizz, fizz, 7 ] )
        self.assertRaises( Exception, l.remove, buzz )
        
    def test_str(self):
        class Foo:
            def __str__(self):
                return "<Foo>"
        self.assertEqual( str(Foo()), "<Foo>" )

    @unittest.skip
    @unittest.expectedFailure
    def test_fail(self):
        self.assertEqual( 1, 2 )        
    
class TestMatrixSolve(unittest.TestCase):
    def test_normalised_constraint(self):
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        self.assertEqual( solve.normalised_constraint_for( 2*a + 6*b , a ), a + 3*b )
        self.assertEqual( solve.normalised_constraint_for( 6*b - 2*a , a ), a - 3*b )

    def test_reduce_constraint_by_equ_at_var(self):
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        self.assertEqual( solve.reduce_constraint_by_equ_for_var( (2*a+b==0), (b==-1), b ), (2*a==1) )
        self.assertEqual( solve.reduce_constraint_by_equ_for_var( (b==-1), (a+b==0), a ), (b==-1) )
        
    def test_canonical(self):
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        c = pylogram.Var('c')
        d = pylogram.Var('d')
        variables_ab = (a+b).variables()
        variables_abc = (a+b+c).variables()
        variables_abcd = (a+b+c+d).variables()
        self.assertEqual(canonical( [ 2*a==1 ]                 ).constraints(), [ a==0.5 ] )
        self.assertEqual(canonical( [ 2*a==1, 1*b==0 ]         ).constraints(), [ a==0.5, b==0 ] )
        self.assertEqual(canonical( [ 2*a==1, 1*b==0 ]         ).constraints(), [ a==0.5, b==0 ] )
        self.assertEqual(canonical( [ 2*a+b==5, a+b==4 ]       ).constraints(), [ a==1, b==3 ] )
        self.assertEqual(canonical( [ a==1, a==1 ]             ).constraints(), [ a==1 ] )
        self.assertEqual(canonical( [ 3*a==3, 7*a==7 ]         ).constraints(), [ a==1 ] )
        self.assertEqual(canonical( [ 2*a+2*c==6, 3*a+3*b==6 ] ).constraints(), [ a+c==3, b-c==-1 ] )
        self.assertEqual(canonical( [ a+b+c+d==1, a+b-c-d==2 ] ).constraints(), [ a+b==1.5, c+d==-0.5 ] )
        self.assertEqual(canonical( [ a+b+c+d==1,-a+b-c+d==2 ] ).constraints(), [ c+a==-0.5, d+b==1.5 ] )
        self.assertRaises( pylogram.Contradiction, canonical, [ a==1, a==2 ]        )
        self.assertRaises( pylogram.Contradiction, canonical, [ a==b, a==-b, a==1 ] )

class TestHelpers(unittest.TestCase):
    def test_nonzero_dict(self):
        d = nonzero_dict(); self.assertEqual( len(d), 0 )
        d[5] = d[5] + 1; self.assertEqual( len(d), 1 ); self.assertEqual( d.keys(), {5} )
        d[5] = d[5] - 1; self.assertEqual( len(d), 0 ); self.assertEqual( d.keys(), set() )
        d[4] += 1; self.assertEqual( len(d), 1 ); self.assertEqual( d.keys(), {4} )
        d[4] -= 1; self.assertEqual( len(d), 0 ); self.assertEqual( d.keys(), set() )
        d[0] = 15
        self.assertEqual( tuple( d.values() ), (15,) )
        self.assertEqual( tuple( d.items() ), ( (0,15), ) )
        d[0] = 0
        self.assertEqual( tuple( d.values() ), () )
        self.assertEqual( tuple( d.items() ), () )

class TestPylogram(unittest.TestCase):
    def setUp(self):
        pylogram.reset_internals()
        
    def test_indepentent_systems(self):
        v1 = pylogram.Varset()
        v1.a [:]= 2 * v1.b
        v1.b [:]= 1
        v2 = pylogram.Varset()
        v2.a [:]= 2 * v2.b
        v2.b [:]= 1
        v3 = pylogram.Varset()
        v3.a [:]= 2 * v3.b
        v3.b [:]= 1
        
    def test_expr_repr(self):
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        self.assertEqual( repr(a-1),"a - 1" )
        self.assertEqual( repr(2*a-1),"2.a - 1" )
        self.assertEqual( repr(a-b),"a - b" )
        self.assertEqual( repr(a-2*b),"a - 2.b" )
        self.assertEqual( repr(-a+2),"-a + 2" )
        self.assertEqual( repr(Fraction(1,2)*a),"a/2" )
        self.assertEqual( repr(Fraction(3,2)*a),"3.a/2" )
        self.assertEqual( repr(Fraction(1,1)*a),"a" )
        
    def test_diophantus_simple(self):
        varset = pylogram.Varset()
        varset.a [:]= 2 * varset.b
        varset.b [:]= 1

        age_at = pylogram.Varset()
        
        #pylogram._solve_debug_print = print
        
        # Fails with too-deep recursion if all the following is uncommented because of order of variables solved for:
        age_at.sons_birth
        age_at.marriage    [:]= age_at.puberty + age_at.death / 7
        age_at.sons_birth  [:]= age_at.marriage + 5
        
    def test_diophantus_constraints(self):
        age_at = Struct()
        # age_at.death = pylogram.Var()
        # age_at.adolescence = pylogram.Var()
        # age_at.marriage = pylogram.Var()
        # age_at.sons_birth = pylogram.Var()
        # age_at.sons_death = pylogram.Var()
        # 
        # age = age_at.death
        # sons_age = age_at.sons_death - age_at.sons_birth
        # 
        # pylogram.constrain( age_at.adolescence == age / 6                        )
        # pylogram.constrain( age_at.puberty     == age_at.adolescence + age / 12  )
        # pylogram.constrain( age_at.marriage    == age_at.puberty + age / 7       )
        # 
        # # age_at.sons_birth  [:]= age_at.marriage + 5
        # # sons_age [:]= age / 2
    
    def test_diophantus_square_equals(self):
        age_at = pylogram.Varset()
        # 
        # age = age_at.death
        # sons_age = age_at.sons_death - age_at.sons_birth
        # 
        # age_at.adolescence [:]= age / 6
        # age_at.puberty     [:]= age_at.adolescence + age / 12
        # age_at.marriage    [:]= age_at.puberty + age / 7
        # 
        # # age_at.sons_birth  [:]= age_at.marriage + 5
        # # sons_age [:]= age / 2
        
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
        
    def _test_is_undef(self,xxx):
        self.assertEqual( pylogram.evaluate(xxx), pylogram.undefined() )
        self.assertEqual( str(xxx), 'undefined' )
        self.assertEqual( xxx.evaluate(), pylogram.undefined() )
        self.assertEqual( str(xxx.evaluate()), 'undefined' )
        self.assertFalse( xxx.is_def() )
        self.assertEqual( xxx.name_or_value(), xxx.name() )

    def _test_evaluates_to(self,xxx, val):
        self.assertEqual( pylogram.evaluate(xxx), val )
        self.assertTrue( isinstance(pylogram.evaluate(xxx), Number) )
        self.assertEqual( xxx, val )
        self.assertTrue( xxx.is_def() )
        self.assertEqual( xxx.evaluate(), val )
        self.assertEqual( xxx.val(), val )
        self.assertEqual( str(xxx), str(val) )
        self.assertEqual( xxx.name_or_value(), str(val) )
        
    def test_syntax_square_equals(self):
        varset = pylogram.Varset()
        self._test_is_undef(varset.a)
        varset.a [:]= 2 * varset.b
        self._test_is_undef(varset.a)
        varset.b [:]= 1
        self._test_evaluates_to( varset.b, 1 )
        self._test_evaluates_to( varset.a, 2 )
        self.assertRaises( pylogram.Contradiction, varset.b.constrain_equal, 2 )

    def test_syntax_constrain(self):
        system = pylogram.System()
        a = pylogram.Var()
        system.constrain( 3==a*2 )
        pylogram.constrain( a == 15 )
        self.assertEqual( system.evaluate(a), 1.5 )
        self.assertEqual( pylogram.evaluate(a), 15 )
        
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
        self.assertFalse( (a+0).is_null() )
        self.assertTrue( pylogram.Expr(0).is_null() )
        self.assertEqual( system.evaluate( a==b ), pylogram.undefined() )
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
    
    def test_contradictions(self):
        system = pylogram.System()
        a = pylogram.Var('a')
        self.assertFalse( system.evaluate( a-a==2 ) )
        self.assertFalse( system.try_constrain(a-a==2) )
        self.assertRaises( pylogram.Contradiction, system.constrain, a-a==2 )

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
        
    def test_variable_creation(self):
        varset = pylogram.Varset()
        system = pylogram.System()
        system2 = pylogram.System()
        self.assertEqual( varset.aaa.name() , 'aaa' )
        system.constrain( varset.aaa == varset.bbb * 2)
        self.assertFalse( system.solved() )
        system.constrain( varset.bbb == 2 )
        self.assertEqual( system.evaluate(varset.bbb), 2)
        self.assertEqual( system.evaluate(varset.aaa), 4)
        ccc = pylogram.Var('ccc')
        system2.constrain( varset.aaa + ccc == 5 )
        self.assertEqual( system2.variables(), {varset.aaa, ccc} )
        
        # for v in varset:
        #     # Should fail until we implement iterating through variables?
        #     pass
            
        a, b, c = varset.make_n(3)
        d = varset.make()
        self.assertTrue( hash(a) < hash(b) < hash(c) < hash(d) )
        self.assertEqual( (a+b+c+d).variables(), {a,b,c,d} )

    def test_system(self):
    
        # Variables
        a = pylogram.Var('a')
        b = pylogram.Var('b')
        
        system = pylogram.System()
        system2 = pylogram.System()

        # Not necessary for real code, but test results expect this order
        self.assertTrue( hash(a) < hash(b) )
        self.assertTrue( list({ a:2, b:1 }.keys())[0] is a )

        # Check we can apply constraints, including duplicates
        system.constrain( b == a * 2 )
        system.constrain( b == 2 * a )
        system.constrain( -1 * b == 0 - (2 * a) )
        
        system2.constrain( a == 1 )

        self.assertEqual( system2.variables(), {a} )
        self.assertEqual( system.variables(), {a,b} )

        self.assertFalse( system.solved() )
        self.assertEqual( system.evaluate(a), pylogram.undefined() )
        self.assertEqual( system.evaluate(b), pylogram.undefined() )

        # Check solution
        system.constrain( a == 3 )
        self.assertTrue( system.solved() )
        
        # Check results
        self.assertEqual( system.evaluate(a), 3 )
        self.assertEqual( system.evaluate(b), 6 )
        self.assertEqual( system.evaluate(2*b), 12 )
        
        a == 2 
        system.constrain( b == a * 2 )

from pylogram_draw import *

class TestDraw(unittest.TestCase):
    def setUp(self):
        pylogram.reset_internals()
        
    def test_ints(self):
        obj1 = Obj()
        obj1.x = 1
        self.assertTrue( isinstance( obj1.x, Number) )
        self.assertEqual( obj1.x, 1 )
        with self.assertRaises(Contradiction): obj1.x = 2
     
    def test_obj(self):
        obj1 = Obj()
        obj1.x = Var()
        obj1.y = Var()
        obj1.x = obj1.y # Create constraint
        obj1.x = 2
        self.assertEqual( obj1.y, 2)
        
    def test_obj_assignment(self):
        pt1 = Point()
        pt2 = Point()
        pt1.x = 3
        self.assertEqual( len(pylogram.default_sys().constraints()), 1 )
        pt2.y = pt2.x * 2
        self.assertEqual( len(pylogram.default_sys().constraints()), 2 )
        pt2 [:]= pt1
        self.assertEqual( len(pylogram.default_sys().constraints()), 4 )
        self.assertTrue( pylogram.default_sys().solved() )
        self.assertEqual( pt1.x, 3 )
        self.assertEqual( pt1.y, 6 )
        self.assertEqual( pt2.x, 3 )
        self.assertEqual( pt2.y, 6 )
        
    def test_lollypop(self):
        class Lollypop:
            def __init__(self):
                self.stick = Line()
                self.circ = Circle()
                self.circ.bottom = self.stick.pt1
                self.stick.pt1.x = self.stick.pt2.x
                line_height = self.stick.pt2.y - self.stick.pt1.y
                line_height [:]= self.circ.d * 2
                self.bottom = self.stick.pt2
                self.height = line_height + self.circ.d
        lollypop = Lollypop()
        lollypop.bottom = Point(0,0)
        lollypop.height = 6
        # self.assertEqual( lollypop.circ.center , Point(0,5) )
        
if __name__ == '__main__':
    unittest.main()