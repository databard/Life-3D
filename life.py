import numpy, bpy, sys

## Checkalive Function
## ---------------------------------------------------------
## Desc: Given a 3D matrix and a point in said matrix,
##       run a modified game of life simulation, inspecting
##       all the points around point x,y,z
## ---------------------------------------------------------
## Input: matrix: A 3D Numpy array of booleans
##        size: Int defining size (x,y,z) of matrix
##        x,y,z: Pretty self explanatory
## ---------------------------------------------------------
## Output: A value for the next iteration of point x,y,z
## ---------------------------------------------------------
def checkalive(matrix, size, x, y, z):
	count = 0
	for i in range(x-1, x+2, 1):
		for j in range(y-1, y+2, 1):
			for k in range(z-1, z+2, 1):
				if i == x and j == y and k == z:
					pass
				else:
					## Wrap around
					if i == size:
						i = 0
					if j == size:
						j = 0
					if k == size:
						k = 0
					count += int(matrix[i,j,k])
	### Rules for Dead Points
	if matrix[x,y,z] == False:
		## If 10 exactly are alive, come to life
		#if count == 4:
		if count >=2 and count <=4:
			return True
		else:
			return False
	### Rules for Live Points
	else:
		if count >= 3 and count <= 8:
			return True
		else:
			return False 

## Iterate Function
## ---------------------------------------------------------
## Desc: Given a 3D matrix and a number of iterations to 
##       iterations to run through, produce the final
##       iteration of the game of life simulation
## ---------------------------------------------------------
## Input: matrix: A 3D Numpy array of booleans
##        size: Int defining size (x,y,z) of matrix
##        numiter: Number of iterations to run
## ---------------------------------------------------------
## Output: The resulting boolean matrix
## ---------------------------------------------------------
def iterate(matrix, size, numiter):
	for iter in range(numiter):
		transfer = numpy.zeros((size,size,size), dtype=bool)
		for i in range(size):
			for j in range(size):
				for k in range(size):
					transfer[i,j,k] = checkalive(matrix, size, i,j,k)
		matrix = transfer
	return matrix

## Populate Function
## ---------------------------------------------------------
## Desc: Create the points and faces needed to generate a
##       3D Object
## ---------------------------------------------------------
## Input: matrix: A 3D Numpy array of booleans
##        size: Int defining size (x,y,z) of matrix
## ---------------------------------------------------------
## Output: A list of (x,y,z) points and a list of points to
##         connect via their indicies in the first list
## ---------------------------------------------------------
def populate(matrix, size):
	points = []
	faces =[]
	const = numpy.sqrt(1/4.0)
	for i in range(size):
		for j in range(size):
			for k in range(size):
				if matrix[i,j,k] == True:
					x,y,z = i-size/2, j-size/2, k-size/2
					## Make all the points in the cube
					newpoints = [
						(x+const, y+const, z+const),
						(x+const, y+const, z-const),
						(x-const, y+const, z-const),
						(x-const, y+const, z+const),
						(x+const, y-const, z+const),
						(x+const, y-const, z-const),
						(x-const, y-const, z-const),
						(x-const, y-const, z+const),
						]
					points.extend(newpoints)
					## Grab the last 8 point indices
					p = range(len(points)-8, len(points))
					## Create all the necessary faces
					newfaces = [
						(p[0],p[1],p[2],p[3]),
						(p[4],p[5],p[6],p[7]),
						(p[0],p[4],p[5],p[1]),
						(p[1],p[5],p[6],p[2]),
						(p[2],p[6],p[7],p[3]),
						(p[3],p[0],p[4],p[7]),
						]
					faces.extend(newfaces)
	return points, faces

## Make Materials Function
def makeMaterial(diffuse):
	mat = bpy.data.materials.new("Material")
	mat.diffuse_color = diffuse
	mat.diffuse_shader = 'LAMBERT' 
	mat.diffuse_intensity = 1.0 
	mat.specular_color = (0,0,0)
	mat.specular_shader = 'COOKTORR'
	mat.specular_intensity = 0
	mat.alpha = 1
	mat.ambient = 1
	return mat

## Set Materials Function
def setMaterial(ob, mat):
	me = ob.data
	me.materials.append(mat)

size = 8
matrix = numpy.zeros((size,size,size), dtype=bool)
## Take input from commandline
ip = (sys.argv[6])
print(ip)
val = []

## Get bits from IP address
[val.extend(list(bin(int(x)+256)[3:])) for x in "{0}".format(ip).split('.')]
for i in range(2):
	for j in range(4):
		for k in range(4):
			matrix[1+j,1+k,3+i] = bool(int(val[i*16+j*4+k]))


points, faces = populate(iterate(matrix,size,3),size)

## BLENDER STUFF FROM BLENDER TUTORIAL
me = bpy.data.meshes.new("conway")   # create a new mesh  
 
ob = bpy.data.objects.new("conway", me)          # create an object with that mesh
ob.location = bpy.context.scene.cursor_location   # position object at 3d-cursor
bpy.context.scene.objects.link(ob)                # Link object to scene
 
# Fill the mesh with verts, edges, faces 
me.from_pydata(points,[],faces)   # edges or faces should be [], or you ask for problems
me.update(calc_edges=True)    # Update mesh with new data

## Make material
ipbits = [int(i)/255.0 for i in ip.split(".")]
blue = makeMaterial((ipbits[0],ipbits[1],ipbits[2]))
setMaterial(ob,blue)

## Render Scene
bpy.data.scenes["Scene"].render.filepath = '//%s' % (ip)
bpy.ops.render.render( write_still=True ) 
