"""
This script is simulating the AC-OPF for DERs using pyomo library

"""
import pandapower as pp
import pandapower.networks as pn
import pandas as pd
# Import libraries
from pyomo.environ import *

# Define paths
pth = r'C:\Users\Dell\Documents\GitHub\PINNS_OPF\data\interim'
con = r'\asset_cons.csv'
ess = r'\asset_ess.csv'
gen = r'\asset_gen.csv'
pv  = r'\asset_pv.csv'
bus = r'\bus5.csv'
line= r'\line5.csv'
time= r'\time_slots.csv'

# Load data
df_con = pd.read_csv(pth+con)
df_ess = pd.read_csv(pth+ess)
df_gen = pd.read_csv(pth+gen)
df_pv  = pd.read_csv(pth+pv)
df_bus = pd.read_csv(pth+bus)
df_line= pd.read_csv(pth+line)
df_time= pd.read_csv(pth+time)



# Network Data
# Buses
Ob = [df_bus.loc[i,'name'] for i in df_bus.index]
Vmin = [df_bus.loc[i,'min_vm_pu'] for i in df_bus.index]
Vmax = [df_bus.loc[i,'max_vm_pu'] for i in df_bus.index]



# Branches
Ol = {(df_line.loc[i, 'from_bus'], df_line.loc[i, 'to_bus']) for i in df_line.index}  # Branch nodes
R = {(df_line.loc[i, 'from_bus'], df_line.loc[i, 'to_bus']): df_line.loc[i, 'r_ohm_per_km']  for i in df_line.index}                                    # Branch PVistance in pu
X = {(df_line.loc[i, 'from_bus'], df_line.loc[i, 'to_bus']): df_line.loc[i, 'x_ohm_per_km'] for i in df_line.index}                                    # Branch reactance in pu
Imax = {(df_line.loc[i, 'from_bus'], df_line.loc[i, 'to_bus']): df_line.loc[i, 'max_i_ka'] for i in df_line.index}



# DGs
Odg = [df_gen.loc[i, 'bus'] for i in df_gen.index]                                      # Nodes with DG
DG_Pmin = {Odg[i]: df_gen.loc[i, 'min_p_mw'] for i in df_gen.index}                          # Minimum active power DG
DG_Pmax = {Odg[i]: df_gen.loc[i, 'max_p_mw'] for i in df_gen.index}                          # Maximum active power DG
DG_fp_min = {Odg[i]: df_gen.loc[i, 'fp_min'] for i in df_gen.index}                      # Minimum power factor DG
DG_ramp_up = {Odg[i]: df_gen.loc[i, 'ramp_up'] for i in df_gen.index}                                # ramp up constraint
DG_ramp_dw = {Odg[i]: df_gen.loc[i, 'ramp_down'] for i in df_gen.index}                                # ramp down constraint
DG_a = {Odg[i]: df_gen.loc[i, 'DG_a'] for i in df_gen.index}                                # Quadratic coefficient cost DG


# PV
Opv = [df_pv.loc[i, 'PV_node'] for i in df_pv.index]                                  # Nodes with PV
PV_pf = {Opv[i]: df_pv.loc[i, 'PV_pf'] for i in df_pv.index}                         # Power factor PV
PV_sn = {Opv[i]: df_pv.loc[i, 'PV_sn'] for i in df_pv.index}                         # Per unit subsidy
PV_Pmin = {Opv[i]: df_pv.loc[i, 'PV_min'] for i in df_pv.index}                     # Minimum power PV
PV_Pmax = {Opv[i]: df_pv.loc[i, 'PV_max'] for i in df_pv.index}                     # Maximum power PV
PV_Pnom = {Opv[i]: df_pv.loc[i, 'PV_Pnom'] for i in df_pv.index}                     # Maximum power PV

# CONSUMERS
Ocons = [i+1 for i in df_con.index]                              # Nodes with flexible CONSUMERS
CONS_nodes = {Ocons[i]: df_con.loc[i, 'Node_cons'] for i in df_con.index}                     # Minimum power CONS
CONS_Pmin = {Ocons[i]: df_con.loc[i, 'CONS_Pmin'] for i in df_con.index}                     # Minimum power CONS
CONS_Pmax = {Ocons[i]: df_con.loc[i, 'CONS_Pmax'] for i in df_con.index}                     # Maximum power CONS
CONS_an = {Ocons[i]: df_con.loc[i, 'CONS_an'] for i in df_con.index}                     # Instantaneous cost load shifted
CONS_bn = {Ocons[i]: df_con.loc[i, 'CONS_bn'] for i in df_con.index}                     # Extra cost load unsatisfied
PD = {Ocons[i]: df_con.loc[i, 'PDn'] for i in df_con.index}                       # Nominal nodal active demand in pu
QD = {Ocons[i]: df_con.loc[i, 'QDn']  for i in df_con.index}                       # Nominal nodal reactive demand in pu
CONS_pf = {Ocons[i]: df_con.loc[i, 'CONS_pf'] for i in df_con.index}                  # Minimum power factor CONS



# Energy storage systems (ESS)
Oess = [df_ess.loc[i, 'ESS_node'] for i in df_ess.index]                                      # Nodes with ESS
ESS_Pmin = {Oess[i]: df_ess.loc[i, 'ESS_Pmin'] for i in df_ess.index}                      # Minimum power ESS
ESS_Pmax = {Oess[i]: df_ess.loc[i, 'ESS_Pmax'] for i in df_ess.index}                      # Maximum power ESS
ESS_Pnom = {Oess[i]: df_ess.loc[i, 'ESS_Pnom'] for i in df_ess.index}                      # Nominal power ESS
ESS_pf_min = {Oess[i]: df_ess.loc[i, 'ESS_pf_min'] for i in df_ess.index}                  # Minimum power factor ESS
ESS_EC = {Oess[i]: df_ess.loc[i, 'ESS_EC'] for i in df_ess.index}                          # Energy capacity ESS
ESS_SOC_ini = {Oess[i]: df_ess.loc[i, 'ESS_SOC_ini']/100 for i in df_ess.index}                # Initial state of charge ESS
ESS_SOC_end = {Oess[i]: df_ess.loc[i, 'ESS_SOC_end']/100 for i in df_ess.index}                # Initial state of charge ESS
ESS_dn = {Oess[i]: df_ess.loc[i, 'ESS_dn'] for i in df_ess.index}                          # Battery  degradation cost ESS
ESS_SOC_min = {Oess[i]: df_ess.loc[i, 'SOC_min']/100 for i in df_ess.index}                        # Minimum state of charge ESS
ESS_SOC_max = {Oess[i]: df_ess.loc[i, 'SOC_max']/100 for i in df_ess.index} 

# # Electric vehicles (EV)
# Oev = [i+1 for i in df_ev.index]                                      # Index EVs
# EV_nodes = {i:df_ev.loc[i-1, 'EV_node'] for i in Oev}                                      # Nodes with EVs
# EV_Pmin = {i:df_ev.loc[i-1, 'EV_Pmin'] for i in Oev}                                  # Minimum power EVs
# EV_Pmax = {i:df_ev.loc[i-1, 'EV_Pmax'] for i in Oev}                                # Maximum power EVs
# EV_Pnom = {i:df_ev.loc[i-1, 'EV_Pnom']/ (Snom) for i in Oev}                               # Nominal power EVs
# EV_pf_min = {i:df_ev.loc[i-1, 'EV_pf_min'] for i in Oev}                              # Minimum power factor EVs
# EV_EC = {i:df_ev.loc[i-1, 'EV_EC']/ (Snom) for i in Oev}                                      # Energy capacity EVs
# EV_SOC_ini = {i:df_ev.loc[i-1, 'EV_SOC_ini']/100 for i in Oev}                            # Arrive state of charge
# EV_SOC_end = {i:df_ev.loc[i-1, 'EV_SOC_end']/100 for i in Oev}                            # Departure state of charge
# EV_SOC_min = {i: df_ev.loc[i-1, 'EV_SOC_min']/100 for i in Oev}                        # Minimum state of charge ESS
# EV_SOC_max = {i: df_ev.loc[i-1, 'EV_SOC_max']/100 for i in Oev}                        # Maximum state of charge ESS
# EV_dn = {i:df_ev.loc[i-1, 'EV_dn'] for i in Oev}                                      # Battery  degradation cost
# EV_wn = {i:df_ev.loc[i-1, 'EV_wn'] for i in Oev}                                      # Penalty  cost  for  not  having  their  battery  charged  at  the desired level
# t_arr = {i:df_ev.loc[i-1, 't_arr'] for i in Oev}                                      # Time of arrival
# t_dep = {i:df_ev.loc[i-1, 't_dep'] for i in Oev}                                      # Time of departure

# time slot data
OT = [df_time.loc[i, 'T'] for i in df_time.index]
sc_res = {OT[i]: df_time.loc[i, 'Irrad'] for i in df_time.index}
Delta_t = {OT[i]: df_time.loc[i, 'Delta_t'] for i in df_time.index}
pt = {OT[i]: df_time.loc[i, 'pt'] for i in df_time.index}

# Demand for consumers and energy by PVs
PM = {(Ocons[i], OT[t]): df_time['PD_{}_{}'.format(df_con['Node_cons'][i],i)][t] for i in df_con.index for t in df_time.index}
QM = {(Ocons[i], OT[t]): df_time['QD_{}_{}'.format(df_con['Node_cons'][i],i)][t] for i in df_con.index for t in df_time.index}
G =  {(Opv[i], OT[t]): df_time['PV_{}_{}'.format(df_pv['PV_node'][i],i)][t] for i in df_pv.index for t in df_time.index}


# Initiate model
model = ConcreteModel()


# Define Sets
model.Ob = Set(initialize=Ob)
model.Ol = Set(initialize=Ol)
model.OT = Set(initialize=OT)
model.Odg = Set(initialize=Odg)
model.Opv = Set(initialize=Opv)
model.Ocons = Set(initialize=Ocons)
model.Oess = Set(initialize=Oess)
#model.Oev = Set(initialize=Oev)
#model.EV_nodes = Param(model.Oev,initialize=EV_nodes, mutable=True)


#- Parameters
# Each resource has upper and lower bounds on active power injection 
# Each resource has power factors
# Generators
model.DG_Pmin = Param(model.Odg, initialize=DG_Pmin, mutable=True)  # Minimum power DGs
model.DG_Pmax = Param(model.Odg, initialize=DG_Pmax, mutable=True)  # Maximum power DGs
model.DG_fp_min = Param(model.Odg, initialize=DG_fp_min, mutable=True)  # Minimum power factor DGs
model.DG_ramp_up = Param(model.Odg, initialize=DG_ramp_up, mutable=True)  # Ramp up constraint
model.DG_ramp_dw = Param(model.Odg, initialize=DG_ramp_dw, mutable=True)  # Ramp down constraint
# PV
model.PV_Pmax = Param(model.Opv,model.OT, initialize=G, mutable=True) # Maximum active power PV
model.PV_Pmin = Param(model.Opv, initialize=PV_Pmin, mutable=True)  # Minimum power PVs
model.PV_Pnom = Param(model.Opv, initialize=PV_Pnom, mutable=True)  # Nominal power PV
model.PV_pf = Param(model.Opv, initialize=PV_pf, mutable=True)  # Constant power factor PVs
model.G = Param(model.Opv, model.OT, initialize=G, mutable=True) # Maximum active power for PVs 
# Consumers
model.CONS_nodes = Param(model.Ocons, initialize=CONS_nodes, mutable=False) # Reactive power bus demand
model.CONS_Pmin = Param(model.Ocons, initialize=CONS_Pmin, mutable=True)  # Minimum power CONS
model.CONS_Pmax = Param(model.Ocons, initialize=CONS_Pmax, mutable=True)  # Maximum power CONS
model.CONS_pf = Param(model.Ocons, initialize=CONS_pf, mutable=True)  # Constant power factor CONS
model.PM = Param(model.Ocons,model.OT, initialize=PM, mutable=True) # Active power demand for CONS
model.CONS_an = Param(model.Ocons, initialize=CONS_an, mutable=True)  # quadratic component cost CONS

# Storage
model.ESS_Pmin = Param(model.Oess, initialize=ESS_Pmin, mutable=True)  # Minimum power ESS
model.ESS_Pmax = Param(model.Oess, initialize=ESS_Pmax, mutable=True)  # Maximum power ESS
model.ESS_Pnom = Param(model.Oess, initialize=ESS_Pnom, mutable=True)  # Nominal power ESS
model.ESS_pf_min = Param(model.Oess, initialize=ESS_pf_min, mutable=True)  # Minimum power factor ESS
model.ESS_SOC_end = Param(model.Oess, initialize=ESS_SOC_end, mutable=True)  # Final state of charge ESS
model.ESS_SOC_ini = Param(model.Oess, initialize=ESS_SOC_ini, mutable=True)  # Initial state of charge ESS
model.ESS_SOC_min = Param(model.Oess, initialize=ESS_SOC_min, mutable=True)  # Minimum state of charge ESS
model.ESS_SOC_max = Param(model.Oess, initialize=ESS_SOC_max, mutable=True)  # MAximum state of charge ESS
model.ESS_dn = Param(model.Oess, initialize=ESS_dn, mutable=True)  # Depretiation cost ESS
model.ESS_EC = Param(model.Oess, initialize=ESS_EC, mutable=True)  # Energy capacity ESS
# EVs - TODO


# A resource can be dispatched at any level given descision variable x_{n,t} - Variables
# Generatos
model.dg_x =  Var(model.Odg, model.OT, initialize=1.0, within=NonNegativeReals)    # Multiplier demands Generators (0,1)
# Consumers
model.cons_x = Var(model.Ocons, model.OT, initialize=1.0, within=NonNegativeReals)    # Multiplier demands CONSUMERS (0,1)
# PV
model.pv_x = Var(model.Opv, model.OT, initialize=1.0, within=NonNegativeReals)    # Multiplier demands PV (0,1)
# Storage
model.ess_x = Var(model.Oess, model.OT, initialize=1.0, within=NonNegativeReals)    # Multiplier demands PV (0,1)
# EVs - TODO

# Each resource has a reactive power injection - Variable
# Generators
model.Qdg = Var(model.Odg, model.OT, within=Reals) # Reactive power for Generators 
# Consumers
model.Qcons = Var(model.Ocons, model.OT, within=NonNegativeReals) # Reactive power for CONSUMERS
# PVs
model.Qpv = Var(model.Opv, model.OT, within=Reals)
# Storage
model.Qess = Var(model.Oess,model.OT, initialize=0.0) 


# ESS - Energy of storage
model.SOC = Var(model.Oess,model.OT, initialize=1.0)    # Reactive power from ESS

# PV
model.PV_sn = Param(model.Opv, initialize=PV_sn, mutable=True)  # Compensation RES


model.Delta_t = Param(model.OT, initialize=Delta_t, mutable=True)  # Time interval
model.pt = Param(model.OT, initialize=pt, mutable=True)  # Wholesale market price

# Cost 
# Generators
model.DG_cost = Var(model.Odg, initialize=1.0)    # cost DG
model.DG_a = Param(model.Odg, initialize=DG_a, mutable=True)  # Quadratic coefficient cost DGs
# Consumers
model.CONS_cost = Var(model.Ocons, initialize=1.0) 
# PV
model.PV_cost = Var(model.Opv, initialize=1.0)    # Multiplier demands CONSUMERS (0,1)
# ESS
model.ESS_cost = Var(model.Oess, initialize=1.0)    # Reactive power from ESS

# Create rules for active and reactive power 
# Generators
# Create rules for active - reactive power

#####################
# ----- DGs -------- #
def DG_constr_active_power_rule(model, i, t):
    return (model.DG_Pmin[i], model.dg_x[i,t]*model.DG_Pmax[i], model.DG_Pmax[i])
model.DG_constr_active_power = Constraint(model.Odg, model.OT,
                                    rule=DG_constr_active_power_rule)  # Minimum, Maximum power from DG

def DG_constr_reactive_power_rule(model, i, t):
    return (-model.dg_x[i,t]*model.DG_Pmax[i]*tan(acos(model.DG_fp_min[i])) <= model.Qdg[i,t])
model.DG_constr_reactive_power = Constraint(model.Odg, model.OT,
                                    rule=DG_constr_reactive_power_rule)  # Minimum, Maximum power from DG

def DG_constr_reactive_power_rule_2(model, i, t):
    return (model.Qdg[i,t] <= model.dg_x[i,t]*model.DG_Pmax[i]*tan(acos(model.DG_fp_min[i])))
model.DG_constr_reactive_power_2 = Constraint(model.Odg, model.OT,
                                       rule=DG_constr_reactive_power_rule_2)  # Minimum, Maximum power from DG
  
def DG_ramp_rule(model, i, t):
    if t > 1:
        return (model.DG_ramp_dw[i]*model.DG_Pmax[i], model.dg_x[i,t]*model.DG_Pmax[i] - model.dg_x[i,t-1]*model.DG_Pmax[i] ,model.DG_ramp_up[i]*model.DG_Pmax[i])
    else:
        return (model.DG_ramp_dw[i] * model.DG_Pmax[i], model.dg_x[i,t]*model.DG_Pmax[i],
                model.DG_ramp_up[i] * model.DG_Pmax[i])
model.DG_ramp = Constraint(model.Odg,model.OT,
                            rule=DG_ramp_rule)  # Minimum, Maximum power from DG

#####################
# ----- CONSUMERS -------- #
def CONS_constr_active_power_rule(model, i, t):
    return (model.CONS_Pmin[i] * model.PM[i,t], model.cons_x[i,t] * model.PM[i,t], model.CONS_Pmax[i] * model.PM[i,t])
model.CONS_constr_active_power = Constraint(model.Ocons, model.OT,
                                    rule=CONS_constr_active_power_rule)  # Minimum, Maximum power from DG

def CONS_constr_reactive_power_rule(model, i, t):
    return (model.cons_x[i,t] * model.PM[i,t]*tan(acos(model.CONS_pf[i])) == model.Qcons[i,t])
model.CONS_constr_reactive_power = Constraint(model.Oess, model.OT,
                                    rule=CONS_constr_reactive_power_rule)  # Reactive power from CONS


#####################
# ----- PV -------- #
def PV_constr_active_power_rule(model, i, t):
    return (model.PV_Pmin[i] * model.G[i,t], model.pv_x[i,t] * model.G[i,t] , model.G[i,t])
model.PV_constr_active_power = Constraint(model.Opv, model.OT,
                                    rule=PV_constr_active_power_rule)  # Minimum, Maximum power from DG

def PV_constr_reactive_power_rule(model, i, t):
    return (model.pv_x[i,t] * model.G[i,t]*tan(acos(model.PV_pf[i])) == model.Qpv[i,t])
model.PV_constr_reactive_power = Constraint(model.Opv, model.OT,
                                    rule=PV_constr_reactive_power_rule)  # Reactive power from CONS


#####################
# ----- ESS -------- #
def ESS_constr_active_power_rule(model, i, t):
    return (model.ESS_Pmin[i]*model.ESS_Pnom[i], model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i], model.ESS_Pmax[i]*model.ESS_Pnom[i])
model.ESS_constr_active_power = Constraint(model.Oess, model.OT,
                                    rule=ESS_constr_active_power_rule)  # Minimum, Maximum power from ESS

def ESS_constr_reactive_power_rule(model, i, t):
    return (-model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i]*tan(acos(model.ESS_pf_min[i])) <= model.Qess[i,t])
model.ESS_constr_reactive_power = Constraint(model.Oess, model.OT,
                                    rule=ESS_constr_reactive_power_rule)  # Minimum, Maximum reactive power from ESS

def ESS_constr_reactive_power_rule_2(model, i, t):
    return (model.Qess[i,t] <= model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i]*tan(acos(model.ESS_pf_min[i])))
model.ESS_constr_reactive_power_2 = Constraint(model.Oess, model.OT,
                                    rule=ESS_constr_reactive_power_rule_2)  # Minimum, Maximum reactive power from ESS


def ESS_constr_SOC_1_rule(model, i, t):
    if t == 1:
        return (model.SOC[i,t] == model.ESS_SOC_ini[i] - model.Delta_t[t]/model.ESS_EC[i]*model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i])
    else:
        return (model.SOC[i,t] == model.SOC[i,t-1] - model.Delta_t[t]/model.ESS_EC[i]*model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i])
model.ESS_constr_SOC_1 = Constraint(model.Oess, model.OT,
                                    rule=ESS_constr_SOC_1_rule)  # Charging

def ESS_constr_SOC_2_rule(model, i, t):
    return (model.ESS_SOC_min[i], model.SOC[i,t], model.ESS_SOC_max[i])
model.ESS_constr_SOC_2 = Constraint(model.Oess, model.OT,
                                    rule=ESS_constr_SOC_2_rule)  # Minimum, Maximum capacity of storage

def ESS_constr_SOC_departure_rule(model, i):
    return (model.ESS_SOC_ini[i] - sum(model.Delta_t[t]/model.ESS_EC[i]*model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i] for t in model.OT) >= model.ESS_SOC_end[i])
model.ESS_constr_SOC_departure = Constraint(model.Oess,
                                    rule=ESS_constr_SOC_departure_rule)  # Minimum, Maximum reactive power from ESS


#######################
# ---- EVs ------- # - TO DO



#### Cost functions ###########

# Generators
def DG_cost_rule(model, i):
    return (model.DG_cost[i] == sum(model.DG_a[i] *  (model.dg_x[i,t]*model.DG_Pmax[i]) ** 2 +  model.pt[t] *  model.dg_x[i,t]*model.DG_Pmax[i]  for t in model.OT)
)
model.DG_cf = Constraint(model.Odg,
                                    rule=DG_cost_rule)  

# Consumers
def CONS_cost_rule(model, i):
    return (model.CONS_cost[i] == sum(sum(model.pt[t]*model.cons_x[i, t]*model.PM[i, t] + model.CONS_an[i] * (model.PM[i, t]) ** 2 * (1 - model.cons_x[i, t]) ** 2 for t in model.OT) for i in model.Ocons )) 
model.CONS_cf = Constraint(model.Ocons,
                                    rule=CONS_cost_rule)  

# PV 
def PV_cost_rule(model, i):
    return (model.PV_cost[i] ==  sum((model.pt[t] + model.PV_sn[i])*model.pv_x[i, t]*model.G[i, t] for t in model.OT))
model.PV_cf = Constraint(model.Opv, rule=PV_cost_rule)  

# ESS
def ESS_cost_rule(model, i):
    return (model.ESS_cost[i] == sum(-model.ESS_dn[i]*(model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i])/model.ESS_EC[i] - model.pt[t]*model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i] for t in model.OT))
model.ESS_cf = Constraint(model.Oess,
                                    rule=ESS_cost_rule)  # Minimum, Maximum reactive power from ESS



#### Parameters for the network
# Define Parameters
#model.Vnom = Param(initialize=Vnom, mutable=True)   # Base voltage magnitude
#model.Snom = Param(initialize=Snom, mutable=True)   # Base apparent power
#model.Tb = Param(model.Ob, initialize=Tb, mutable=True) # Type of bus (1 - Slack, 0 - Load)
model.Vmin = Param(model.Ob, initialize=Vmin, mutable=True)   # Minimum voltage magnitude
model.Vmax = Param(model.Ob, initialize=Vmax, mutable=True)   # Maximum voltage magnitude
model.R = Param(model.Ol, initialize=R, mutable=True) # Line resistance
model.X = Param(model.Ol, initialize=X, mutable=True) # Line reactance
model.Imax = Param(model.Ol, initialize=Imax, mutable=True) # Maximum current magnitude

#### Variables for the network
# Define Variables
model.P = Var(model.Ol, model.OT, initialize=0) # Acive power flowing in lines
model.Q = Var(model.Ol, model.OT, initialize=0) # Reacive power flowing in lines
model.I  = Var(model.Ol, model.OT, initialize=0) # Current of lines
model.V = Var(model.Ob, model.OT, initialize=0.0, within=NonNegativeReals) 



def active_power_flow_rule(model, k,t):
        return ((sum(model.P[j,i,t] for j,i in model.Ol if i == k )
                 + sum(model.dg_x[i,t]*model.DG_Pmax[i] for i in model.Odg if k == i) + sum(model.ess_x[i,t]*model.ESS_Pmax[i]*model.ESS_Pnom[i] for i in model.Oess if k == i)
                 + sum(model.pv_x[i,t] * model.G[i,t] for i in model.Opv if k==i) + sum(model.cons_x[i,t] * model.PM[i,t] for i in model.Ocons if k==model.CONS_nodes[i])) == 
                  sum(model.P[i,j,t] + model.R[i,j]*(model.I[i,j,t]) for i,j in model.Ol if k == i))
model.active_power_flow = Constraint(model.Ob, model.OT, rule=active_power_flow_rule)   # Active power balance

def reactive_power_flow_rule(model, k,t):
        return (sum(model.Q[j,i,t] for j,i in model.Ol if i == k ) - sum(model.Q[i,j,t] + model.X[i,j]*(model.I[i,j,t]) for i,j in model.Ol if k == i) +
                sum(model.Qdg[i,t] for i in model.Odg if k == i) + sum(model.Qess[i,t] for i in model.Oess if k==i)
                + sum(model.Qpv[i,t] for i in model.Opv if k==i) + sum(model.Qcons[i,t] for i in model.Ocons if k==model.CONS_nodes[i])== 0)   
model.reactive_power_flow = Constraint(model.Ob, model.OT, rule=reactive_power_flow_rule) # Reactive power balance

def voltage_drop_rule(model, i, j,t):
    return (model.V[i,t] - 2*(model.R[i,j]*model.P[i,j,t] + model.X[i,j]*model.Q[i,j,t]) - (model.R[i,j]**2 + model.X[i,j]**2)*model.I[i,j,t] - model.V[j,t] == 0)
model.voltage_drop = Constraint(model.Ol, model.OT, rule=voltage_drop_rule) # Voltage drop

def define_current_rule (model, i, j, t):
    return ((model.I[i,j,t])*(model.V[j,t]) <= model.P[i,j,t]**2 + model.Q[i,j,t]**2)
model.define_current = Constraint(model.Ol, model.OT, rule=define_current_rule) # Power flow

def voltage_limit_rule(model,i,t):
    return (model.Vmin[i] , model.V[i,t], model.Vmax[i])
model.voltage_limit = Constraint(model.Ob, model.OT, rule = voltage_limit_rule)


# Define Objective Function
def act_loss(model):
    return  (sum(model.CONS_cost[i] for i in model.Ocons)
            + sum(model.DG_cost[i] for i in model.Odg)
            + sum(model.ESS_cost[i] for i in model.Oess)
            - sum(model.PV_cost[i] for i in model.Opv))
model.obj = Objective(rule=act_loss)

# Run model 
solver = SolverFactory("gurobi")
solver.options['NonConvex'] = 2
solver.solve(model)
model.display()