from transportation.vector_math import R2Vector, R3Vector, angle_between

# Vettori 2D
v1 = R2Vector(x=3, y=4)
v2 = R2Vector(x=1, y=2)
print(v1 + v2)        # (4, 6)
print(v1.norm())      # 5.0

# Vettori 3D
v3 = R3Vector(x=1, y=0, z=0)
v4 = R3Vector(x=0, y=1, z=0)
print(v3.cross(v4))   # (0, 0, 1)
