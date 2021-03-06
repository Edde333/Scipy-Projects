# -*- coding: utf-8 -*-
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
"""
This class is used to calculate a spline using a blossom algorithm. 
"""


class d_spline:
    
    
    def __init__(self, k, u):
        """
        Creates an object which is used to calculate the spline values.
        Parameters
        ----------
        k : Int
            The order of the spline (for example 1D, 2D, 3D...)
        u : Array (1xK-4)
            The chosen u-values of the spline
        d : Array (1xK-4)
            The chosen control points of the spline

        Returns
        -------
        None.

        """
        self.k = k
        self.u = u
       
    
    def __call__(self, x, d, g = 3):
        """
        The main function used to calculate the values of the spline
        
        Parameters
        ----------
        x : Float
            The points of interest of the spline. 
         d : Array of floats
            An array of control points for the spline
        g : Int
            Indicates which blossom which will be calculated. For example:
            If k=g=3 is selected d[u,u,u] = s(u) is calculated. While if 
            k=3, g=2 the blossom d[u,u,u_i] is calculated.
            
        Returns
        -------
        An array (1xn), or a matrix (kxn) depending on the dimension of the
        spline. 
            DESCRIPTION.
        """
        #u = self.expandArray(self.u)
        ret = np.zeros((d.ndim,x.shape[0]))
        I = self.findHotInterval(self.u,x)
        # Run dSpline for each row(dimension) of the d matrix.
        if d.ndim > 1:
            for dimension in range(d.ndim):
                currd = d[dimension]
                left = I
                right = I+1
                depth = 0
                ret[dimension] = self.dRecursive(x, currd, left, right, g)
        else: 
            left = (I+g-self.k)
            right = I+1
            depth = 0
            return self.dRecursive(x, d, left, right, g)
        return ret


    # def expandArray(self, u):
    #     """
    #     Expands the vector u by prepending k-1 elements equal to the first
    #     element in u, and appends k-1 elements equal to the last element in u.
    #     Effectively turns the original u vector (k,K-4) -> (k,K)
        
    #     Parameters
    #     ----------
    #     u : Array of floats (1,K-4)
    #         The vector that will be expanded

    #     Returns
    #     -------
    #     u : Array of floats (1,K)
    #         The extended Array u:
    #         [u1, u2, ... , uK-3, uK-2] -> 
    #         [u1, u1, u1, u2, u3, ... , uK-3, uK-2, uK-2, uK-2]
    #         |------| <-------- k-1 times --------> |---------|

    #     """
    #     u = np.insert(u, 0, np.ones(self.k-1)*u[0])
    #     u = np.append(u,np.ones(self.k-1)*u[-1])
    #     return u
    
    
    def findHotInterval(self, u, x):
        """
        Calculates the hot interval for the point x.

        Parameters
        ----------
        u : Array of floats (1xK)
            The array of knots u_i.
        x : Array of floats (1xK)
            The array of points x_i to be evaluated

        Returns
        -------
        I : Array of ints.
            The array I contains the indices of the
            hot interval in the array u containing
            the knots.

        """
        I = np.zeros(len(x), dtype = 'int8')
        for i in range(len(x)):
            index = np.argmax(u >= x[i]) - 1
            if index < self.k-1: index = self.k-1
            I[i] = index
        return I
    
    
    def dRecursive(self, x, d, left, right, g):
        """
        The recursive step of the blossom algorithm
        
        Parameters
        ----------
        x : Array of floats (1xK)
            The array of points x_i to be evaluated
        I : Array of ints.
            The array I contains the indices of the
            hot interval in the array u containing
            the knots.
        d : Array of floats
            An array of control points for the spline
        depth : Int
            Indicates at which depth of the recursion
            the current function is at
        left : Int
            The index of the left-most knot in the 
            interval I
        right : Int
            The index of the right-most knot in the
            interval I
        g : Int
            Indicates which blossom which will be calculated. For example:
            If k=g=3 is selected d[u,u,u] = s(u) is calculated. While if 
            k=3, g=2 the blossom d[u,u,u_i] is calculated.
            
        Returns
        -------
        The left-most value if in the deepest layer of recursion, else
        the calculated value for the given values in x.
        """
        if np.any(right-left == g+1):
            return d[left+1]
        a = self.alpha(x,left, right)
        d0 = self.dRecursive(x, d, left - 1, right, g)
        d1 = self.dRecursive(x, d, left, right + 1, g)
        return a*d0 + (1-a)*d1
        
    
    def alpha(self, x, left, right):
        """
        Generates the values of alpha which are used to 
        calculate the values of x in the blossom algorithm.

        Parameters
        ----------
        x : Array of floats (1xK)
            The array of points x_i to be evaluated
       left : Int
            The index of the left-most knot in the 
            interval I
        right : Int
            The index of the right-most knot in the
            interval I

        Returns
        -------
        alph : FLoat
            Returns the value of alpha which is used to generate
            the values of x in the blossom algorithm

        """
        alphdivider = (self.u[right]-self.u[left])
        zeroValues = np.where(alphdivider == 0)
        alphdivider[zeroValues] = 1
        alph = (self.u[right] - x)/alphdivider
        alph[zeroValues] = 0
        return alph
    
    def plot(self, D,plot_options = ['spline', 'control points'] ):
        u_min = min(self.u)
        u_max = max(self.u)
        
        fig, ax = plt.subplots(1,1)

        if 'spline' in plot_options:
            u_intervall = np.linspace(u_min, u_max,1000*int(u_max-u_min)+1)
            vals = self.__call__(u_intervall, D, g = 3)
            graph = ax.plot (vals[0], vals[1], 'r-', label='spline')

        if 'control points' in plot_options:
            u_intervall = self.u.copy()
            vals = self.__call__(u_intervall, D, g = 3)
            graph = ax.plot (D[0], D[1], color = 'k', linestyle = 'dotted', marker = 'o')

        plt.show()
        
     
if __name__ == '__main__':
            
    CONTROL = [(-12.73564, 9.03455),
    (-12.73564, 9.03455),
    (-12.73564, 9.03455),
    (-26.77725, 15.89208),
    (-42.12487, 20.57261),
    (-15.34799, 4.57169),
    (-31.72987, 6.85753),
    (-49.14568, 6.85754),
    (-38.09753, -1e-05),
    (-67.92234, -11.10268),
    (-89.47453, -33.30804),
    (-21.44344, -22.31416),
    (-32.16513, -53.33632),
    (-32.16511, -93.06657),
    (-2e-05, -39.83887),
    (10.72167, -70.86103),
    (32.16511, -93.06658),
    (21.55219, -22.31397),
    (51.377, -33.47106),
    (89.47453, -33.47131),
    (15.89191, 0.00025),
    (30.9676, 1.95954),
    (45.22709, 5.87789),
    (14.36797, 3.91883),
    (27.59321, 9.68786),
    (39.67575, 17.30712),
    (39.67575, 17.30712),
    (39.67575, 17.30712)]
    
    D = np.array(CONTROL).T
    U_min = 0
    U_max = 1
    U = np.linspace(U_min, U_max, 25*(U_max-U_min)+1)
    U = np.insert(U,0, [0,0])
    U = np.insert(U,-1, [1,1])
    #u = np.linspace(U_min, U_max,1000*(U_max-U_min)+1)

    dspline = d_spline(3, U)  
    
    dspline.plot(D)
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    