# HumanRegistration
Build a skeleton using Blender and register it to human mesh.

![img](./img/skeleton.png)

You can edit the skeleton and add a new mesh (obtained from scanner, e.g. PhotoScan) in ```HumanRegistration.blend```. Here, we use SMPL template as example.

Then, run the ```export.py``` in Blender to export the parameters.

```main.py``` shows a demo of LBS (Linear Blending Skinning) for registered human.

![img](./img/lbs.png)