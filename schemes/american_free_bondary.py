import logging

from scipy.sparse.linalg import spsolve
from scipy.sparse import coo_matrix
from numpy import zeros


def free_boundary(A, x, y, b, ob, free_bdry_guess, dtype=float):
  """
  solves the elliptic variational inequality arising when discretizing the black and Scholes equations for american options by a one step time scheme
  /* ob : a vector describing  the obstacle function */
  /* x : the unknown function */
  /* y : auxiliary function */
  /* A the matrix of the problem */
  /* b the right hand side */
  /* free_bdry_guess : guess for the position of the free boundary*/
  /* it should come from the previous time step */

  const  MatriceProfile<T_numtype> & A,
  KN<T_numtype> & x,  KN<T_numtype> & y,
  const  KN<T_numtype> & b, const  KN<T_numtype> & ob,
  int & free_bdry_guess
  """
  found = iterations = sense_of_motion = 0
  fbpos = free_bdry_guess
  #/* y contains b-A * ob */
  #/* recall that the constraint b-A*x <= 0*/
  #/* is to be satisfied */
  #/* so the contact zone is a subset of the region b-A*ob <=0 */ 
  y = ob * A.tocsr()
  y -= b
  y *= -1.
  A = A.todense()

  # fst_ineq_threshold is the extremal point of the zone  b-A*ob < 0
  fst_ineq_threshold = 0
  while y.item(fst_ineq_threshold + 1) < 0:
    fst_ineq_threshold += 1

  logging.info("found fst_ineq_threshold  %d" % fst_ineq_threshold)
  while not found and abs(float(fbpos - free_bdry_guess)) < 150 and iterations < 150:
    iterations += 1
    prev_sense_of_motion = sense_of_motion

    #we shall solve a dirichlet problem in the zone i>= fbpos
    matsize = len(x) - fbpos

    # fills the matrix and RHS
    xaux = zeros(matsize, dtype=dtype)

    row = []
    col = []
    data = []

    for i in xrange(0, matsize):
      row += [i]
      col += [i]
      data += [A[i + fbpos, i + fbpos] if i > 0 else 1.]
      #print "%d %d %d %s %s" % (i, i, fbpos,  auxmat[i,i], b[i+fbpos])
      xaux[i] = b[i + fbpos]

    #auxmat[0,0] = 1.
    for i in xrange(0, matsize - 1):
      row += [i, i + 1]
      col += [i + 1, i]
      data += [A[i + fbpos, i + fbpos + 1] if i > 0 else 0., A[i + fbpos + 1, i + fbpos]]

    auxmat = coo_matrix((data, (row, col)), shape=(matsize, matsize)).tocsr()
    xaux[0] = ob[fbpos]
    logging.info("fills the matrix and RHS done")

    #solves the system
    xaux = spsolve(auxmat, xaux)

    #checks if the guess for the free boundary is correct
    #if not, proposes a new guess
    found = 1

    #checks the inequality b>= ob
    if xaux[1] < ob[fbpos + 1]:
      fbpos += 1
      found = 0
      sense_of_motion = 1
    else:
      #check the inequality A*x>= b
      aux = dtype(A[fbpos, fbpos] * ob[fbpos] + A[fbpos, fbpos - 1] * ob[fbpos - 1] + A[fbpos, fbpos + 1] * xaux[1])
      #print aux, b[fbpos], fbpos-1, fst_ineq_threshold
      logging.info("check inequality done")
      if aux < b[fbpos]:
        found = 0
        fbpos -= 1
        sense_of_motion = -1
      elif fbpos - 1 > fst_ineq_threshold:
        found = 0
        fbpos -= 1
        sense_of_motion = -1

    not_infinite_loop = sense_of_motion * prev_sense_of_motion

    if not_infinite_loop == -1:
      logging.warning("enters an infinite loop")
      found = 1

    #the guess is correct, saves the solution in the vector x
    if found == 1:
      x[0:fbpos] = ob[0:fbpos]
      x[fbpos:len(ob)] = xaux[0: len(ob) - fbpos]

  logging.info(
    "found fbpos %d; deviation initial position %d; iterations %d" % (fbpos, fbpos - free_bdry_guess, iterations)
  )

  if float(fbpos - free_bdry_guess) < 150 and iterations < 150:
    return fbpos
  else:
    return -10
