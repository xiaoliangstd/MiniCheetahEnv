import numpy as np

class mini_cheetah():
    def __init__(self,pybullet_client):
        self.pybullet_client = pybullet_client

        model_path = 'gym-MiniCheetahEnv/gym_MiniCheetahEnv/envs/rsc/mini_cheetah/mini_cheetah.urdf'

        self.leg_tags = ['_fr_','_fl_','_hl_','_hr_']        
        self._robot_init_pos =[0,0,0.4]
        self._robot_init_ori = [0, 0, 0, 1]
        self.prev_feet_points = np.ndarray((5,3))        
        
        self.robot = self.pybullet_client.loadURDF(model_path, self._robot_init_pos,self._robot_init_ori)
        self.pybullet_client.resetBasePositionAndOrientation(self.robot, self._robot_init_pos, self._robot_init_ori)
        self.pybullet_client.resetBaseVelocity(self.robot, [0, 0, 0], [0, 0, 0])
        self._joint_name_to_id, self._motor_id_list  = self._build_motor_id_list()
        self._reset_legs()


    def _get_base_position(self):
        return self.pybullet_client.getBasePositionAndOrientation(self.robot)

    def _get_base_velocity(self):
        return self.pybullet_client.getBaseVelocity(self.robot)
    
    
    
    def _build_motor_id_list(self):
        num_joints = self.pybullet_client.getNumJoints(self.robot)
        joint_name_to_id = {}
        for i in range(num_joints):
            joint_info = self.pybullet_client.getJointInfo(self.robot, i)
            joint_name_to_id[joint_info[1].decode("UTF-8")] = joint_info[0]


        MOTOR_NAMES = [     "torso_to_abduct_fr_j",
                            "abduct_fr_to_thigh_fr_j",
                            "thigh_fr_to_knee_fr_j",

                            "torso_to_abduct_fl_j",
                            "abduct_fl_to_thigh_fl_j",
                            "thigh_fl_to_knee_fl_j",

                            "torso_to_abduct_hr_j",
                            "abduct_hr_to_thigh_hr_j",
                            "thigh_hr_to_knee_hr_j",

                            "torso_to_abduct_hl_j",
                            "abduct_hl_to_thigh_hl_j",
                            "thigh_hl_to_knee_hl_j"
                        ]

        motor_id_list = [joint_name_to_id[motor_name] for motor_name in MOTOR_NAMES]

        return joint_name_to_id, motor_id_list

    def _reset_legs(self,standstilltorque=10):       

        for leg in self.leg_tags:

            #Abduction Motor
            self.pybullet_client.resetJointState(self.robot,
			self._joint_name_to_id['torso_to_abduct'+leg+'j'],
			targetValue=0, targetVelocity=0)
            
            #Hip Motor
            self.pybullet_client.resetJointState(self.robot,
			self._joint_name_to_id['abduct'+leg+'to_thigh'+leg+'j'],
			targetValue=-0.67, targetVelocity=0)

            #Hip Motor
            self.pybullet_client.resetJointState(self.robot,
			self._joint_name_to_id['thigh'+leg+'to_knee'+leg+'j'],
			targetValue=1.25, targetVelocity=0)

            # To provide a certain standstill torque
            self.pybullet_client.setJointMotorControlArray(
			bodyIndex=self.robot,
			jointIndices=[self._joint_name_to_id['torso_to_abduct'+leg+'j'],
                          self._joint_name_to_id['abduct'+leg+'to_thigh'+leg+'j'],
                          self._joint_name_to_id['thigh'+leg+'to_knee'+leg+'j']
                         ],
			controlMode=self.pybullet_client.VELOCITY_CONTROL,
			targetVelocities=[0,0,0],
			forces=[standstilltorque]*3)

    def _apply_motor_torques(self,torques):
        torques_per_leg = {self.leg_tags[0],torques[0:3],
                           self.leg_tags[1],torques[3:6],
                           self.leg_tags[2],torques[6:9],
                           self.leg_tags[3],torques[9:12]}

        for leg in self.leg_tags:
            self.pybullet_client.setJointMotorControlArray(
			bodyIndex=self.robot,
			jointIndices=[self._joint_name_to_id['torso_to_abduct'+leg+'j'],
                          self._joint_name_to_id['abduct'+leg+'to_thigh'+leg+'j'],
                          self._joint_name_to_id['thigh'+leg+'to_knee'+leg+'j']
                         ],
			controlMode=self.pybullet_client.TORQUE_CONTROL,
			forces=torques_per_leg[leg])

    def _set_on_rack(self):
        self.pybullet_client.createConstraint(
				self.robot, -1, -1, -1, self.pybullet_client.JOINT_FIXED,
				[0, 0, 0], [0, 0, 0], [0, 0, 0.5])