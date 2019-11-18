#!/usr/bin/python

import numpy as np
import open3d as o3d
import cv2
import copy
import math

param={
  'radius_normal':2.0,
  'radius_feature':5.0,
  'maxnn_normal':30,
  'maxnn_feature':100,
  'distance_threshold':1.5,
  'icp_threshold':0.002
}

def trimRT(mat):
  M=np.hstack((mat,np.array([0,0,0]).reshape((3,1))))
  M=np.vstack((M,np.array([0,0,0,1]).reshape((1,4))))
  return M
def toNumpy(pcd):
  return np.reshape(np.asarray(pcd.points),(-1,3))
def fromNumpy(dat):
  d=dat.astype(np.float32)
  pc=o3d.PointCloud()
  pc.points=o3d.Vector3dVector(d)
  return pc
def transform(T,P):
  return np.dot(T,np.vstack((P.T,np.ones((1,len(P)))))).T[:,:3]
def getImmovTf(T,p0):
  p1=transform(T,p0)
  pc0=fromNumpy(p0)
  pc1=fromNumpy(p1)
  reg=o3d.registration_icp(pc1,pc0,param['icp_threshold'],np.eye(4,dtype=float),o3d.TransformationEstimationPointToPoint())
#  print reg.fitness
#  print reg.transformation
  return np.dot(reg.transformation,T),p1
def getwTx(N,P):
#  wTx=np.array([],dtype=float).reshape((4,4,-1))
#  wTx=np.dstack([wTx,np.eye(4,dtype=float)])
#  wTx=np.stack([wTx,np.eye(4,dtype=float)])
  wTx=[]
  wTx.append(np.eye(4,dtype=float))
  for i in range(1,N):
    theta=2*np.pi*i/N
    cos=np.cos(theta)
    sin=np.sin(theta)
    wTwi=np.eye(4,dtype=float)
    wTwi[0,0]=cos;wTwi[0,1]=sin
    wTwi[1,0]=-sin;wTwi[1,1]=cos
    print "transform by Wi"
    wTxi,pcn=getImmovTf(wTwi,P)
#    wTx=np.dstack([wTx,wTxi])
    wTx.append(wTxi)
    print "transform by Xi"
    getImmovTf(wTxi,P)
  return np.asarray(wTx)

items=[]
pcd0=o3d.read_point_cloud("surface.ply")
pcd0.paint_uniform_color([1, 0.706, 0])
items.append(pcd0)
P0=toNumpy(pcd0)
g0=np.mean(P0,axis=0)
mTw=np.eye(4,dtype=float)
mTw[0,3]=g0[0]
mTw[1,3]=g0[1]
mTw[2,3]=g0[2]

N=3

for i in range(2):
  Pw=transform(np.linalg.inv(mTw),P0)  #move points to axis center
  wTx=getwTx(N,Pw)
  print "wTx",i,wTx
  zbase=wTx[:,:,2][:,:3]
  zmean=np.mean(zbase,axis=0)
  zmean=zmean/np.linalg.norm(zmean)
  print "zmean",zmean
  zcross=np.cross(wTx[0,:,2][:3],zmean)  #angle would be small enough to aproximate as sin
  print "zcross",zcross
  rod,jaco=cv2.Rodrigues(zcross)
  rod=trimRT(rod)
  obase=wTx[:,:,3]
  omean=np.mean(obase,axis=0)
  print "omean",omean
  rod[:,3]=omean
  print "rod",rod
  mTw=np.dot(mTw,rod)

sTs=[]
sTs.append(mTw)
for i in range(1,N):
  sTs.append(np.dot(np.dot(mTw,wTx[i]),np.linalg.inv(mTw)))
  Px=transform(sTs[i],P0)
  pcx=fromNumpy(Px)
  pcx.paint_uniform_color([0,0.6,0.4*i])
  items.append(pcx)

print np.asarray(sTs)

points=[[0,0,0],np.ravel(mTw[:3,3]), np.ravel(mTw[:3,3])-np.ravel(mTw[:3,2])*0.1]
lines=[[0,1],[1,2]]
colors = [[0,0,1],[1,0,0]]
line_set = o3d.geometry.LineSet()
line_set.points = o3d.utility.Vector3dVector(points)
line_set.lines = o3d.utility.Vector2iVector(lines)
line_set.colors = o3d.utility.Vector3dVector(colors)
items.append(line_set)
o3d.visualization.draw_geometries(items)