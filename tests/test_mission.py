import math
import unittest
import numpy as np
from scene.animation import Mission,State,DURATIONS
from scene.camera_controls import Camera

class MissionTests(unittest.TestCase):
    def test_consistency_across_frame_rates(self):
        outputs=[]
        for fps in (20,30,60,144):
            m=Mission()
            for _ in range(fps*82): m.update(1/fps)
            outputs.append((m.state.value,m.elapsed,m.cycles,m.pose().rover_x,m.pose().shoulder))
        for row in outputs[1:]: np.testing.assert_allclose(row,outputs[0],atol=1e-9)

    def test_pause_keeps_camera_operational(self):
        m=Mission(); m.update(10); before=m.pose(); m.paused=True
        camera=Camera(); old=camera.position.copy(); yaw=camera.yaw
        for _ in range(120):
            m.update(1/60); camera.update(1/60,{'w':True,'right':True})
        self.assertEqual(m.pose(),before); self.assertEqual(m.total,10)
        self.assertGreater(np.linalg.norm(camera.position-old),1)
        self.assertNotEqual(camera.yaw,yaw)
        m.paused=False; m.update(2); self.assertEqual(m.state,State.EXCAVATOR_WORKING)

    def test_interaction_order_and_two_cycles(self):
        m=Mission(); m.update(sum(DURATIONS)*2+.5)
        self.assertEqual(m.cycles,2); self.assertEqual(m.state,State.ROVER_EXPLORING)
        expected=[s.name for s in State]
        self.assertEqual([a for a,b in m.transitions],expected*2)

    def test_rover_waits_for_excavator(self):
        for t in np.linspace(6.1,25.9,150):
            m=Mission(); m.update(float(t)); self.assertAlmostEqual(m.pose().rover_x,-2.2)
        m=Mission(); m.update(28); self.assertGreater(m.pose().rover_x,-2.2)

    def test_reset_restores_pose(self):
        a=Mission(); b=Mission(); b.update(83.2); b.paused=True; b.reset()
        self.assertEqual(a.pose(),b.pose()); self.assertFalse(b.paused)

    def test_invalid_dt(self):
        for value in (-1,math.inf,math.nan):
            with self.assertRaises(ValueError): Mission().update(value)

    def test_mouse_orientation(self):
        c=Camera(); old=c.forward.copy(); c.update(0,{},(100,-50))
        self.assertGreater(np.linalg.norm(c.forward-old),.1)
        c.update(5,{'up':True}); self.assertLessEqual(c.pitch,1.45)

if __name__=='__main__': unittest.main()
