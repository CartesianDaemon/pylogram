#! python

# Standard libraries
import unittest
import os

# Pylogram libraries
import pylogram

class TestPylogram(unittest.TestCase):
    def test_numbers(self):
    
        # Variables
        a = pylogram.Var()
        b = pylogram.Var()
        
        system = pylogram.System()

        # Not necessary for real code, but test results expect this order
        self.assertTrue( hash(a) < hash(b) )
        self.assertTrue( { a:1, b:2 }.keys()[0] is a )

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
        
        # Check we can apply constraints, including duplicates
        system.constrain_equals( b , a * 2 )
        system.constrain_equals( b , 2 * a )
        system.constrain_equals( -1 * b , 0 - (2 * a) )

        self.assertFalse( system.solved() )

        system.constrain_equals( a , 3 )
        
        # Get values
        system.solved()
        system.solved_value(a)
        system.solved_value(b)
        
        # Check intermediates
        self.assertIs( system.x()[0], a )
        self.assertIs( system.x()[1], b )
        self.assertEquals( system.A(), ((-2,1),(-2,1),(2,-1),(1,0)) )
        self.assertEquals( system.b(), (0,0,0,3) )
        self.assertTrue( system.solved() )
        
        # Check results
        self.assertEquals( system.solved_value(a), 3 )
        self.assertEquals( system.solved_value(b), 6 )
        self.assertRaises( AssertError, system.solved_value, 2 )
        self.assertRaises( AssertError, system.solved_value, a == b )
        # Not sure which to use:
        #   self.assertEquals( solved_value( 2 * b ), 12 )
        #   self.assertRaises( AssertError, solved_value, 2 * b )
        
        # a == 2 
        # system.constrain( b == a * 2 )

if __name__ == '__main__':
    unittest.main(verbosity=2)