from pyplc.config import plc
from sys import platform
from concrete import Factory,Motor,MSGate,Container,Dosator,Weight,Mixer,Readiness,Loaded,Manager,Lock
from concrete.elevator import ElevatorGeneric as Elevator
from concrete.vibrator import Vibrator
from concrete.container import Retarder
from concrete.imitation import iELEVATOR,iGATE,iVALVE,iMOTOR,iWEIGHT
from collections import namedtuple
from pyplc.utils.misc import TOF,TON
from pyplc.utils.trig import RTRIG
from pyplc.utils.latch import RS
from pyplc.pou import POU

class MOVE(POU):
  en = POU.input(False,hidden=True)
  q  = POU.output(False,hidden=True)
  def __init__(self,en=True,i=None,q=None,id: str=None,parent:POU=None):
    super().__init__(id=id,parent=parent)
    self.en = en
    self.i = i
    self.q = q
      
  def __call__(self,en=None,i=None):
      with self:
          en = self.overwrite('en',en)
          i = self.overwrite('i',i)
          
          if en: self.q=i
          
      return self.q

if platform=='vscode':
  PLC = namedtuple('PLC', ('FILLERS_M_1', 'CEMENT_M_1', 'WATER_M_1', 'MIXER_I_1', 'MIXER_ON_1', 'APUMP_ON_1', 'CONVEYOR_ON_1', 'ELEVATOR_UP_1', 'ELEVATOR_DOWN_1', 'VIBRATOR_ON_1', 'VIBRATOR_ON_2', 'VIBRATOR_ON_3', 'S_VIBRATOR_ON_1', 'AUGER_ON_1', 'FILLER_OPEN_1', 'FILLER_OPEN_2', 'FILLER_OPEN_3', 'DCEMENT_OPEN_1', 'WATER_OPEN_1', 'ADDITION_OPEN_1', 'DWATER_OPEN_1', 'MIXER_OPEN_1',
                  'EMERGENCY_ON_1', 'MIXER_ISON_1', 'AUGER_ISON_1', 'CONVEYOR_ISON_1', 'ELEVATOR_RISE_1', 'ELEVATOR_LOWER_1', 'FILLER_CLOSED_1', 'FILLER_CLOSED_2', 'FILLER_CLOSED_3', 'APUMP_ISON_1', 'DCEMENT_CLOSED_1', 'DWATER_CLOSED_1', 'ADDITION_CLOSED_1', 'MIXER_CLOSED_1', 'MIXER_OPENED_1', 'ELEVATOR_BELOW_1', 'ELEVATOR_MIDDLE_1', 'ELEVATOR_ABOVE_1', 'LLEVEL_1', 'HLEVEL_1', 'EMERGENCY_ISON_1'))
  plc=PLC()

factory_1 = Factory( )
motor_1 = Motor(ison=plc.MIXER_ISON_1,powered=plc.MIXER_ON_1)
gate_1 = MSGate(closed = plc.MIXER_CLOSED_1,opened=plc.MIXER_OPENED_1,open=plc.MIXER_OPEN_1)

cement_m_1 = Weight(raw = plc.CEMENT_M_1,mmax=1500)
water_m_1 = Weight(raw = plc.WATER_M_1, mmax=500)
fillers_m_1 = Weight(raw=plc.FILLERS_M_1,mmax=8000)

silage_1 = Container(m=lambda: cement_m_1.m, closed=~plc.AUGER_ON_1,out=plc.AUGER_ON_1, lock=Lock(key=~plc.DCEMENT_CLOSED_1), max_sp=500 )
dcement_1 = Dosator(m=lambda: cement_m_1.m,closed=plc.DCEMENT_CLOSED_1,out=plc.DCEMENT_OPEN_1,containers=(silage_1, ),lock=Lock(key=lambda: plc.AUGER_ON_1 or not plc.MIXER_ISON_1 ) )

water_1 = Container(m=lambda: water_m_1.m,closed=~plc.WATER_OPEN_1,out=plc.WATER_OPEN_1,lock=Lock(key=lambda: plc.ADDITION_OPEN_1 or not plc.DWATER_CLOSED_1),max_sp=300)
addition_1 = Container(m=lambda: water_m_1.m,closed=plc.ADDITION_CLOSED_1,out = plc.ADDITION_OPEN_1,lock=Lock(key=lambda: plc.WATER_OPEN_1 or not plc.DWATER_CLOSED_1),max_sp=50)
apump_1 = TOF(clk:=plc.ADDITION_OPEN_1,q=plc.APUMP_ON_1,pt=3000)
dwater_1 = Dosator(m=lambda: water_m_1.m, out=plc.DWATER_OPEN_1, closed=plc.DWATER_CLOSED_1,containers=(water_1,addition_1),lock=Lock(key=lambda: plc.WATER_OPEN_1 or plc.ADDITION_OPEN_1 or not plc.MIXER_ISON_1))

retarder_1 = Retarder(m = lambda: fillers_m_1.m, outs=(plc.FILLER_OPEN_1,plc.FILLER_OPEN_2,plc.FILLER_OPEN_3),sts=(plc.FILLER_CLOSED_1,plc.FILLER_CLOSED_2,plc.FILLER_CLOSED_3))
filler_1 = Container(m = lambda: fillers_m_1.m, out=retarder_1.out(0),closed=retarder_1.closed(0),lock=Lock(key=lambda: retarder_1.lock(0)))
filler_2 = Container(m = lambda: fillers_m_1.m, out=retarder_1.out(1),closed=retarder_1.closed(1),lock=Lock(key=lambda: retarder_1.lock(1)))
filler_3 = Container(m = lambda: fillers_m_1.m, out=retarder_1.out(2),closed=retarder_1.closed(2),lock=Lock(key=lambda: retarder_1.lock(2)))
vibrator_1 = Vibrator(q=plc.VIBRATOR_ON_1,containers=(plc.FILLER_OPEN_1,),weight=fillers_m_1)
vibrator_2 = Vibrator(q=plc.VIBRATOR_ON_2,containers=(plc.FILLER_OPEN_2,),weight=fillers_m_1)
vibrator_3 = Vibrator(q=plc.VIBRATOR_ON_3,containers=(plc.FILLER_OPEN_3,),weight=fillers_m_1)
conveyor_1 = Dosator(m = lambda: fillers_m_1.m, out=plc.CONVEYOR_ON_1,closed=~plc.CONVEYOR_ISON_1,containers=(filler_1,filler_2,filler_3),lock=Lock(key=lambda: not plc.FILLER_CLOSED_1 or not plc.FILLER_CLOSED_2 or not plc.FILLER_CLOSED_3 or not plc.ELEVATOR_BELOW_1))

elevator_1 = Elevator(above = plc.ELEVATOR_ABOVE_1,below = plc.ELEVATOR_BELOW_1,middle=plc.ELEVATOR_MIDDLE_1,up=plc.ELEVATOR_UP_1,down=plc.ELEVATOR_DOWN_1,containers=(filler_1,filler_2,filler_3),dosator=conveyor_1)

ready_1 = Readiness( (dcement_1,dwater_1,elevator_1) )
loaded_1= Loaded( (dcement_1,dwater_1,elevator_1) )
mixer_1 = Mixer(gate=gate_1,motor=motor_1,flows=(x.q for x in (silage_1,water_1,addition_1)+tuple(elevator_1.expenses) ) )

def load_order():
  elevator_1.unload = True
  while not elevator_1.unloading and not factory_1.emergency:
    yield
  dcement_1.unload = True
  dwater_1.unload = True
  yield

#логика срабатывания сигнала EMERGENCY_ON_1
emergency_delay_1 = TON(clk=lambda: (plc.ELEVATOR_DOWN_1 and not plc.ELEVATOR_LOWER_1) or (plc.ELEVATOR_UP_1 and not plc.ELEVATOR_RISE_1) )  
emergency_trig_1 = RTRIG(clk=lambda: elevator_1.fault or motor_1.error==Motor.E_TIMEOUT or emergency_delay_1() )
emergency_move_1 = RS(set=emergency_trig_1,reset=~plc.EMERGENCY_ON_1, q=plc.EMERGENCY_ON_1)

manager_1 = Manager( collected=ready_1, loaded=loaded_1,mixer=mixer_1,dosators=(dcement_1,dwater_1,conveyor_1,elevator_1),loadOrder=load_order )

factory_1.on_mode = tuple(x.switch_mode for x in (silage_1,water_1,addition_1,filler_1,filler_2,filler_3,dcement_1,dwater_1,conveyor_1))
factory_1.on_emergency = tuple(x.emergency for x in (dcement_1,dwater_1,conveyor_1,elevator_1,mixer_1,manager_1))

instances = (factory_1,motor_1,gate_1,mixer_1,cement_m_1,water_m_1,fillers_m_1,silage_1,water_1,addition_1,filler_1,filler_2,filler_3,dcement_1,dwater_1,conveyor_1,elevator_1,ready_1,loaded_1,manager_1,vibrator_1,vibrator_2,vibrator_3,retarder_1,apump_1,emergency_move_1 )

if platform=='linux':
  imotor_1 = iMOTOR(simple=True,on=plc.MIXER_ON_1,ison=plc.MIXER_ISON_1)
  igate_1 = iGATE(open=plc.MIXER_OPEN_1,opened=plc.MIXER_OPENED_1,closed=plc.MIXER_CLOSED_1,simple=True)
  idcement_1 = iVALVE(open=plc.DCEMENT_OPEN_1,closed=plc.DCEMENT_CLOSED_1)
  idwater_1 = iVALVE(open=plc.DWATER_OPEN_1,closed=plc.DWATER_CLOSED_1)
  iconveyor_1 = iMOTOR(simple=True,on=plc.CONVEYOR_ON_1,ison=plc.CONVEYOR_ISON_1)
  iauger_1 = iMOTOR(simple=True,on=plc.AUGER_ON_1,ison=plc.AUGER_ISON_1)
  iapump_1 = iMOTOR(simple=True,on=plc.APUMP_ON_1,ison=plc.APUMP_ISON_1)
  iaddition_1 = iVALVE(open=plc.ADDITION_OPEN_1,closed=plc.ADDITION_CLOSED_1)
  ifiller_1 = iVALVE(open=plc.FILLER_OPEN_1,closed=plc.FILLER_CLOSED_1)
  ifiller_2 = iVALVE(open=plc.FILLER_OPEN_2,closed=plc.FILLER_CLOSED_2)
  ifiller_3 = iVALVE(open=plc.FILLER_OPEN_3,closed=plc.FILLER_CLOSED_3)
  ielevator_1 = iELEVATOR(up=plc.ELEVATOR_UP_1,down=plc.ELEVATOR_DOWN_1,above=plc.ELEVATOR_ABOVE_1,below=plc.ELEVATOR_BELOW_1,middle=plc.ELEVATOR_MIDDLE_1)
  icement_m_1 = iWEIGHT(speed=100, loading=plc.AUGER_ON_1,unloading=plc.DCEMENT_OPEN_1,q=plc.CEMENT_M_1)
  iwater_m_1 = iWEIGHT(speed=100, loading=lambda: plc.WATER_OPEN_1 or plc.ADDITION_OPEN_1,unloading=plc.DWATER_OPEN_1,q=plc.WATER_M_1)
  ifillers_m_1 = iWEIGHT(speed=100, loading=lambda : plc.FILLER_OPEN_1 or plc.FILLER_OPEN_2 or plc.FILLER_OPEN_3,unloading=plc.CONVEYOR_ON_1,q=plc.FILLERS_M_1)
  ielevator_up_1 = iMOTOR(simple=True,on=plc.ELEVATOR_UP_1,ison=plc.ELEVATOR_RISE_1)
  ielevator_down_1 = iMOTOR(simple=True,on=plc.ELEVATOR_DOWN_1,ison=plc.ELEVATOR_LOWER_1)
    
  instances += (imotor_1,igate_1,idcement_1,idwater_1,iconveyor_1,iauger_1,iapump_1,iaddition_1,ifiller_1,ifiller_2,ifiller_3,ielevator_1,icement_m_1,iwater_m_1,ifillers_m_1,ielevator_up_1,ielevator_down_1)

plc.run( instances=instances, ctx=globals() )
