# TODO: Make run with python, once I've reverted python3 to python

# Standard libraries
import unittest
import os
from fractions import Fraction

# Pylogram libraries
import expressions
import expressions as pyl
import solve
from solve import Canonical
from helpers import *

from tkinter import *

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
        
    def test_tk(self):
        # master = Tk()
        # w = Canvas(master, width=200, height=100)
        # w.pack()
        # w.create_line(0, 0, 200, 100)
        # w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
        # w.create_rectangle(50, 25, 150, 75, fill="blue")
        # mainloop()
        pass
    
class TestMatrixSolve(unittest.TestCase):
    def setUp(self):
        expressions.reset_internals()
        
    def test_normalised_constraint(self):
        a = expressions.Var('a')
        b = expressions.Var('b')
        self.assertEqual( solve.normalised_constraint_for( 2*a + 6*b , a ), a + 3*b )
        self.assertEqual( solve.normalised_constraint_for( 6*b - 2*a , a ), a - 3*b )

    def test_reduce_constraint_by_equ_at_var(self):
        a = expressions.Var('a')
        b = expressions.Var('b')
        self.assertEqual( solve.reduce_constraint_by_equ_for_var( (2*a+b==0), (b==-1), b ), (2*a==1) )
        self.assertEqual( solve.reduce_constraint_by_equ_for_var( (b==-1), (a+b==0), a ), (b==-1) )
        
    def test_canonical(self):
        a = expressions.Var('a')
        b = expressions.Var('b')
        c = expressions.Var('c')
        d = expressions.Var('d')
        variables_ab = (a+b).variables()
        variables_abc = (a+b+c).variables()
        variables_abcd = (a+b+c+d).variables()
        self.assertEqual(Canonical( [ 2*a==1 ]                 ).constraints(), [ a==0.5 ] )
        self.assertEqual(Canonical( [ 2*a==1, 1*b==0 ]         ).constraints(), [ a==0.5, b==0 ] )
        self.assertEqual(Canonical( [ 2*a==1, 1*b==0 ]         ).constraints(), [ a==0.5, b==0 ] )
        self.assertEqual(Canonical( [ 2*a+b==5, a+b==4 ]       ).constraints(), [ a==1, b==3 ] )
        self.assertEqual(Canonical( [ a==1, a==1 ]             ).constraints(), [ a==1 ] )
        self.assertEqual(Canonical( [ 3*a==3, 7*a==7 ]         ).constraints(), [ a==1 ] )
        self.assertEqual(Canonical( [ 2*a+2*c==6, 3*a+3*b==6 ] ).constraints(), [ a+c==3, b-c==-1 ] )
        self.assertEqual(Canonical( [ a+b+c+d==1, a+b-c-d==2 ] ).constraints(), [ a+b==1.5, c+d==-0.5 ] )
        self.assertEqual(Canonical( [ a+b+c+d==1,-a+b-c+d==2 ] ).constraints(), [ c+a==-0.5, d+b==1.5 ] )
        self.assertRaises( expressions.Contradiction, Canonical, [ a==1, a==2 ]        )
        self.assertRaises( expressions.Contradiction, Canonical, [ a==b, a==-b, a==1 ] )

class TestHelpers(unittest.TestCase):
    def setUp(self):
        expressions.reset_internals()
        self.arr_y = list(range(5,10))
        self.arr_x = list(range(5))
        
    def test_each_passthrough(self):
        self.assertEqual( each(self.arr_y)[2], 7 )
        self.assertEqual( each(self.arr_y).val[2], 7 )

    def test_each_assign(self):
        each(self.arr_y).val = each(self.arr_x).val
        self.assertEqual( self.arr_y, [0,1,2,3,4] )
    
    def test_each_double(self):
        each(self.arr_x).__mul__(2)
        each(self.arr_y).val = each(self.arr_x).val * 2
        self.assertEqual( self.arr_y, [0,2,4,6,8] )
    
    def test_each_2x_plus_1(self):
        each(self.arr_y).val = each(self.arr_x) * 2 + 1
        self.assertEqual( self.arr_y, [1,3,5,7,9] )

    def test_each_struct(self):
        class Pt:
            def __init__(self,x=0,y=0):
                self.x, self.y = x,y
        pts = [ Pt(0), Pt(1), Pt(2) ]
        each(pts).y = each(pts).x ** 2
        self.assertEqual( tuple(each(pts).y), (0,1,4) )
        each(pts).y = 1 + each(pts).x * 2
        self.assertEqual( tuple(each(pts).y), (1,3,5) )

    def test_every(self):
        every(self.arr_x).val = 5
        self.assertEqual( self.arr_x, [5]*5 )
    
    def test_prev(self):
        prev(self.arr_x)
        each(self.arr_y).val = prev(self.arr_x)
        self.assertEqual( self.arr_y, [5,0,1,2,3] )

    @unittest.expectedFailure
    def test_prev_idx(self):
        self.assertEqual( prev(self.arr_y)[0], [5] )

    @unittest.expectedFailure
    def test_prev_self(self):
        each(self.arr_y).val = prev(self.arr_y) * 2
        self.assertEqual( self.arr_y, [5,10,20,40,80] )
    
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
    
    def test_reduce_undef_truthvals(self):
        a = expressions.Var('a')
        b = expressions.Var('b')
        self.assertEqual( True & expressions._Undefined() , expressions.undefined() )
        self.assertEqual( False & expressions._Undefined(), False )
        self.assertEqual( expressions._Undefined() & True,  expressions.undefined() )
        self.assertEqual( expressions._Undefined() & False, False)
        self.assertEqual( expressions._Undefined() & expressions._Undefined(), expressions.undefined() )
        self.assertEqual( expressions._Undefined() & expressions._Undefined() & expressions._Undefined(), expressions.undefined() )

        self.assertEqual( (a==a).evaluate(), True )
        self.assertEqual( (a==b).evaluate(), expressions.undefined() )
        self.assertEqual( (a-a==1).evaluate(), False )
        self.assertEqual( (a==a) & (a==a), True )
        self.assertEqual( (a==a) & (a==b), expressions.undefined() )
        self.assertEqual( (a==a) & (a-a==1), False )
        
        self.assertEqual(expressions._Undefined() & (a==b), expressions.undefined())

    def test_more_reduce_undef_truthvals(self):
        a = expressions.Var('a')
        b = expressions.Var('b')
        self.assertEqual( undef_eq([a,1,b],[a,1,b]), True )
        self.assertEqual( undef_eq([a,1,b],[a,a,b]), expressions.undefined() )
        self.assertEqual( undef_eq([a,a,b],[b,b,b]), expressions.undefined() )
        self.assertEqual( undef_eq([a,a,0],[b,b,1]), False )
        self.assertEqual( undef_eq([a,1,1],[a,1,0]), False )
        self.assertEqual( undef_eq([a,a,1],[a,1,0]), False )

    def inverse_mod_n(self):
        p = 101
        for a in range(1, p):
            inv = inverse_mod_n(a, p)
            self.assertEqual( (inv * a) % p, 1 )
        self.assertEqual( inverse_mod_n(570004, None), Fraction(1,570004) )
        self.assertEqual( inverse_mod_n(1, 5), 1 )
        self.assertEqual( inverse_mod_n(8, 5), inverse_mod_n(3, 5) )
        self.assertEqual( inverse_mod_n(-2, 5), inverse_mod_n(3, 5) )
        self.assertEqual( inverse_mod_n(-1, 5), 4 )
        inverse_mod_n(-1, 17)
        
class TestPylogram(unittest.TestCase):
    def setUp(self):
        expressions.reset_internals()
        
    def test_indepentent_systems(self):
        v1 = expressions.Varset()
        v1.a [:]= 2 * v1.b
        v1.b [:]= 1
        v2 = expressions.Varset()
        v2.a [:]= 2 * v2.b
        v2.b [:]= 1
        v3 = expressions.Varset()
        v3.a [:]= 2 * v3.b
        v3.b [:]= 1
        
    def test_expr_repr(self):
        a = expressions.Var('a')
        b = expressions.Var('b')
        self.assertEqual( repr(a-1),"a - 1" )
        self.assertEqual( repr(2*a-1),"2.a - 1" )
        self.assertEqual( repr(a-b),"a - b" )
        self.assertEqual( repr(a-2*b),"a - 2.b" )
        self.assertEqual( repr(-a+2),"-a + 2" )
        self.assertEqual( repr(Fraction(1,2)*a),"a/2" )
        self.assertEqual( repr(Fraction(3,2)*a),"3.a/2" )
        self.assertEqual( repr(Fraction(1,1)*a),"a" )
        
    def test_diophantus_simple(self):
        varset = expressions.Varset()
        varset.a [:]= 2 * varset.b
        varset.b [:]= 1

        age_at = expressions.Varset()
        
        #expressions._solve_debug_print = print
        
        # Fails with too-deep recursion if all the following is uncommented because of order of variables solved for:
        age_at.sons_birth
        age_at.marriage    [:]= age_at.puberty + age_at.death / 7
        age_at.sons_birth  [:]= age_at.marriage + 5
        
    def test_diophantus_constraints(self):
        age_at = Struct()
        # age_at.death = expressions.Var()
        # age_at.adolescence = expressions.Var()
        # age_at.marriage = expressions.Var()
        # age_at.sons_birth = expressions.Var()
        # age_at.sons_death = expressions.Var()
        # 
        # age = age_at.death
        # sons_age = age_at.sons_death - age_at.sons_birth
        # 
        # expressions.constrain( age_at.adolescence == age / 6                        )
        # expressions.constrain( age_at.puberty     == age_at.adolescence + age / 12  )
        # expressions.constrain( age_at.marriage    == age_at.puberty + age / 7       )
        # 
        # # age_at.sons_birth  [:]= age_at.marriage + 5
        # # sons_age [:]= age / 2
    
    def test_diophantus_square_equals(self):
        age_at = expressions.Varset()
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
        undef = expressions._Undefined()
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
        self.assertEqual( expressions.evaluate(xxx), expressions.undefined() )
        self.assertEqual( str(xxx), 'undefined' )
        self.assertEqual( xxx.evaluate(), expressions.undefined() )
        self.assertEqual( str(xxx.evaluate()), 'undefined' )
        self.assertFalse( xxx.is_def() )
        self.assertEqual( xxx.name_or_value(), xxx.name() )

    def _test_evaluates_to(self,xxx, val):
        self.assertEqual( expressions.evaluate(xxx), val )
        self.assertTrue( isinstance(expressions.evaluate(xxx), Number) )
        self.assertEqual( xxx, val )
        self.assertTrue( xxx.is_def() )
        self.assertEqual( xxx.evaluate(), val )
        self.assertEqual( xxx.val(), val )
        self.assertEqual( str(xxx), str(val) )
        self.assertEqual( xxx.name_or_value(), str(val) )
        
    def test_syntax_square_equals(self):
        varset = expressions.Varset()
        self._test_is_undef(varset.a)
        varset.a [:]= 2 * varset.b
        self._test_is_undef(varset.a)
        varset.b [:]= 1
        self._test_evaluates_to( varset.b, 1 )
        self._test_evaluates_to( varset.a, 2 )
        self.assertRaises( expressions.Contradiction, varset.b.constrain_equal, 2 )

    def test_syntax_constrain(self):
        system = expressions.System()
        a = expressions.Var()
        system.constrain( 3==a*2 )
        expressions.constrain( a == 15 )
        self.assertEqual( system.evaluate(a), 1.5 )
        self.assertEqual( expressions.evaluate(a), 15 )
        
    def test_arithmetic(self):
        system = expressions.System()
        a = expressions.Var('a')
        b = expressions.Var('b')
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
        system = expressions.System()
        a = expressions.Var('a')
        b = expressions.Var('b')
        self.assertEqual( system.evaluate( 3) , 3 )
        self.assertEqual( system.evaluate( 3*a +2 -2*a -a ) , 2 )
        self.assertTrue( (a-a).is_null() )
        self.assertFalse( (a+0).is_null() )
        self.assertTrue( expressions.Expr(0).is_null() )
        self.assertEqual( system.evaluate( a==b ), expressions.undefined() )
        self.assertTrue( expressions.Equ( a, a ) )
        self.assertTrue( expressions.Equ( a + b, b + a ) )
        self.assertTrue( a == a )
        self.assertTrue( a + b == b + a )
        self.assertEqual( a, a )
        self.assertEqual( a + b, b + a )
        
    def test_multiple_assignment(self):
        obj = Primitive()
        obj.a = Var()
        obj.b = Var()
        obj.c = Var()
        obj.a = obj.b = obj.c = 3
        self.assertEqual( obj.a.val(), 3)
        self.assertEqual( obj.b.val(), 3)
        self.assertEqual( obj.c.val(), 3)        

    def test_simple_evaluations(self):
        system = expressions.System()
        a = expressions.Var('a')
        b = expressions.Var('b')
        system.constrain( a== 2)
        system.constrain( b== 3)
        self.assertEqual( system.evaluate(expressions.Expr(2)/2), 1 )
        self.assertEqual( system.evaluate(a/2), 1 )
        self.assertEqual( system.evaluate(1*2), 2 )
        with self.assertRaises( TypeError): 1/b
        with self.assertRaises( AssertionError): a/b # TODO: make both use same error type
        self.assertEqual( system.evaluate(a/2), 1 )
        self.assertEqual( system.evaluate(b*2), 6 )
        self.assertEqual( system.evaluate((a+b)*2), 10 )
        self.assertEqual( system.evaluate( a*5 + b/3 -2*(a+b) - (-0.1) ), 1.1 )
    
    def test_contradictions(self):
        system = expressions.System()
        a = expressions.Var('a')
        self.assertFalse( system.evaluate( a-a==2 ) )
        self.assertFalse( system.try_constrain(a-a==2) )
        self.assertRaises( expressions.Contradiction, system.constrain, a-a==2 )

    def test_equ(self):
        system = expressions.System()
        a = expressions.Var()
        b = expressions.Var()
        # self.assertEqual( a==b, b==a )
        self.assertNotEqual( a==a, a==b )
        self.assertEqual( a==a, expressions.Expr(0)==0 )
        self.assertNotEqual( a==a, 0 )
    
    def test_solve(self):
        system = expressions.System()
        a = expressions.Var()
        b = expressions.Var()
        system.constrain( a + b == 3)
        system.constrain( 2 * a + b == 5)
        self.assertTrue( system.solved() )
        self.assertEqual( system.evaluate(a), 2 )
        self.assertEqual( system.evaluate(b), 1 )
        
    def test_variable_creation(self):
        varset = expressions.Varset()
        system = expressions.System()
        system2 = expressions.System()
        self.assertEqual( varset.aaa.name() , 'aaa' )
        system.constrain( varset.aaa == varset.bbb * 2)
        self.assertFalse( system.solved() )
        system.constrain( varset.bbb == 2 )
        self.assertEqual( system.evaluate(varset.bbb), 2)
        self.assertEqual( system.evaluate(varset.aaa), 4)
        ccc = expressions.Var('ccc')
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
        a = expressions.Var('a')
        b = expressions.Var('b')
        
        system = expressions.System()
        system2 = expressions.System()

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
        self.assertEqual( system.evaluate(a), expressions.undefined() )
        self.assertEqual( system.evaluate(b), expressions.undefined() )

        # Check solution
        system.constrain( a == 3 )
        self.assertTrue( system.solved() )
        
        # Check results
        self.assertEqual( system.evaluate(a), 3 )
        self.assertEqual( system.evaluate(b), 6 )
        self.assertEqual( system.evaluate(2*b), 12 )
        
        a == 2 
        system.constrain( b == a * 2 )
        
    def test_mod_eq1(self):
        a = expressions.Var('a')
        equ = (a*2==3).mod(7)
        self.assertEqual( (equ/2).coefficient(a) % 7, 1 )
        self.assertEqual( (equ/2).rhs_constant() % 7, 5 )
        self.assertEqual( equ.solve_for_var(a), 5 )
        self.assertEqual( (a==5).mod(7).solve_for_var(a), 5 )
        self.assertEqual( (a==12).mod(7).solve_for_var(a), 5 )
        self.assertEqual( list( Canonical([ (a*2==3).mod(5) ]) ), [(6*a==9).mod(5)] )
        self.assertEqual( (a==1).mod(3), (a==1).mod(3) )
        self.assertNotEqual( a==1, (a==1).mod(3) )
        expressions.constrain( a*2==3 , mod=5 )
        self.assertEqual( a, 4)

    def test_mod_eq2(self):
        vars = expressions.Varset()
        equ1 =  (   vars.a + 5*vars.b == 22 ).mod(17)
        equ2 =  ( 2*vars.a +   vars.b == -5 ).mod(17)
        cncl = Canonical( [equ1,equ2] 
            # ,print_steps = print
            )
        a_val, b_val = cncl.values()
        self.assertEqual( (a_val+5*b_val)%17 , 22%17 )
        self.assertEqual( (2*a_val+b_val)%17 , (-5)%17 )

from object import *

class TestArray(unittest.TestCase):
    def setUp(self):
        expressions.reset_internals()
        
    def test_arr_var(self):
        arr = Array(6,Var)
        arr.first = 0
        arr.last = 10
        for a,b,c in arr.adj_objs(3): constrain( c-b == b-a )
        self.assertEqual( arr , (0,2,4,6,8,10) )
        
    def test_arr_circ(self):
        arr = Array(2,Circle,"circs")
        # arr.first.left = Point(0,Var())
        # arr.last.right = Point(10,Var())
        arr.first.left.x = 0
        arr.last.right.x = 4
        for a,b in arr.adj_objs():
            a.right = b.left
            a.r = b.r
        self.assertEqual( arr[1].r, 1 )
        self.assertFalse( arr[1].top.y.is_def() )
        self.assertEqual( arr[1].top.y, expressions.undefined() )
        
    def test_arr_props(self):
        arr = Array(3,Point)
        arr.first.x = 3

    def test_arr_init(self):
        Array(3,Var)
        Array(3,Point)
        Array(3,Primitive)
        
class TestObj(unittest.TestCase):
    def setUp(self):
        expressions.reset_internals()
        
    def test_ints(self):
        obj1 = Primitive()
        obj1.x = 1
        self.assertTrue( isinstance( obj1.x, Number) )
        self.assertEqual( obj1.x, 1 )
        with self.assertRaises(Contradiction): obj1.x = 2
     
    def test_obj(self):
        obj1 = Primitive()
        obj1.x = Var()
        obj1.y = Var()
        obj1.x = obj1.y # Create constraint
        obj1.x = 2
        self.assertEqual( obj1.y, 2)
        
    def test_obj_assignment(self):
        pt1 = Point()
        pt2 = Point()
        pt1.x = 3
        self.assertEqual( len(expressions.default_sys().constraints()), 1 )
        pt2.y = pt2.x * 2
        self.assertEqual( len(expressions.default_sys().constraints()), 2 )
        pt2 [:]= pt1
        self.assertEqual( len(expressions.default_sys().constraints()), 4 )
        self.assertTrue( expressions.default_sys().solved() )
        self.assertEqual( pt1.x, 3 )
        self.assertEqual( pt1.y, 6 )
        self.assertEqual( pt2.x, 3 )
        self.assertEqual( pt2.y, 6 )

from draw import *

class TestPrimitives(unittest.TestCase):
    def setUp(self):
        expressions.reset_internals()
        
    def test_points(self):
        p1 = Point()
        p2 = p1 + Point(1,1)
        p3 = p2 + Point(3,3)
        p3 [:] = Point(4,4)
        self.assertTrue( expressions.solved() )
        self.assertEqual( p1.x, 0 )
        self.assertEqual( p1.y, 0 )
        self.assertEqual( p1, Point(0,0) )
        
    def test_pt_init(self):
        p1 = Point(3,4)
        p2 = Point(p1.y,Var())
        p3 = Point(4,44)
        self.assertTrue( pyl.is_num(p1.x) )
        self.assertTrue( pyl.is_num(p1.y) )
        self.assertTrue( pyl.is_num(p2.x) )
        self.assertTrue( pyl.is_var(p2.y) )
        self.assertEqual( p2.x, 4 )
        p2 [:]= p3
        self.assertEqual( p2.y.val(), 44 )
        
    def test_circ(self):
        pass
        
    def test_square(self):
        sq = Square()
        sq.topleft = Point(0,0)
        sq.topright.x = 5
        self.assertEqual(sq.bottomright.y.val(),5)
        
    def test_undef(self):
        p1 = Point()
        p1.x = 3
        self.assertEqual( len(expressions.constraints()), 1 )
        self.assertEqual( expressions.evaluate(p1.x), 3 )
        self.assertEqual( expressions.evaluate(p1.x==3), True )
        self.assertTrue( bool(p1.x==3) )
        self.assertFalse( p1.y.is_def() )
        self.assertEqual( p1==Point(3,3), expressions.undefined() )
        self.assertEqual( p1==Point(0,0), False )
        self.assertEqual( p1==Point(), expressions.undefined() )
        
class TestDraw(unittest.TestCase):
    def setUp(self):
        expressions.reset_internals()
        
    class Lollypop(Primitive):
        def __init__(self):
            self.stick = Line('stick')
            self.circ = Circle('ball')
            self.circ.bottom = self.stick.pt1
            self.stick.pt1.x = self.stick.pt2.x
            line_height = self.stick.pt2.y - self.stick.pt1.y
            line_height [:]= self.circ.d * 2
            self.bottom = self.stick.pt2
            self.height = line_height + self.circ.d
            self.mid = self.circ.bottom

    def test_lollypop_sim(self):
        lollypop = self.Lollypop()
        lollypop.bottom = Point(1,0)
        lollypop.height = 6
        self.assertEqual( lollypop.circ.c == Point(1,-5), True )
        output = lollypop.sim_draw()
        self.assertEqual(len(output.splitlines()),2)
        self.assertEqual(output.count("line"),1)
        self.assertEqual(output.count("circle"),1)

    def test_lollypop_draw(self):
        master = Tk()
        lollypop = self.Lollypop()
        lollypop.mid = Point(150,150)
        lollypop.height = 150
        canvas = Canvas(master, width=300, height=300)
        lollypop.draw(canvas)
        canvas.pack()
        
    @unittest.skip
    def test_display(self):
        self.test_lollypop_draw()
        mainloop()
        
if __name__ == '__main__':
    unittest.main()