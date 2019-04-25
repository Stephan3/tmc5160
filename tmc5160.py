#!/usr/bin/python2

import bus, logging, collections, tmc2130

TMC_FREQUENCY=1000000.

registers = {
"GCONF":          0x00,
"GSTAT":          0x01,
"IFCNT":          0x02,
"SLAVECONF":      0x03,
"INP_OUT":        0x04,
"X_COMPARE":      0x05,
"OTP_PROG":       0x06,
"OTP_READ":       0x07,
"FACTORY_CONF":   0x08,
"SHORT_CONF":     0x09,
"DRV_CONF":       0x0A,
"GLOBAL_SCALER":  0x0B,
"OFFSET_READ":    0x0C,
"IHOLD_IRUN":     0x10,
"TPOWERDOWN":     0x11,
"TSTEP":          0x12,
"TPWMTHRS":       0x13,
"TCOOLTHRS":      0x14,
"THIGH":          0x15,
"RAMPMODE":       0x20,
"XACTUAL":        0x21,
"VACTUAL":        0x22,
"VSTART":         0x23,
"A1":             0x24,
"V1":             0x25,
"AMAX":           0x26,
"VMAX":           0x27,
"DMAX":           0x28,
"D1":             0x2A,
"VSTOP":          0x2B,
"TZEROWAIT":      0x2C,
"XTARGET":        0x2D,
"VDCMIN":         0x33,
"SWMODE":         0x34,
"RAMPSTAT":       0x35,
"XLATCH":         0x36,
"ENCMODE":        0x38,
"XENC":           0x39,
"ENC_CONST":      0x3A,
"ENC_STATUS":     0x3B,
"ENC_LATCH":      0x3C,
"ENC_DEVIATION":  0x3D,
"MSLUT0":         0x60,
"MSLUT1":         0x61,
"MSLUT2":         0x62,
"MSLUT3":         0x63,
"MSLUT4":         0x64,
"MSLUT5":         0x65,
"MSLUT6":         0x66,
"MSLUT7":         0x67,
"MSLUTSEL":       0x68,
"MSLUTSTART":     0x69,
"MSCNT":          0x6A,
"MSCURACT":       0x6B,
"CHOPCONF":       0x6C,
"COOLCONF":       0x6D,
"DCCTRL":         0x6E,
"DRVSTATUS":      0x6F,
"PWMCONF":        0x70,
"PWMSCALE":       0x71,
"PWM_AUTO":       0x72,
"LOST_STEPS":     0x73
}

#
fields = {}

fields["GCONF"] = {
	"RECALIBRATE":	0x01 << 0 ,
	"FASTSTANDSTILL":	0x02 << 1 ,
	"EN_PWM_MODE":	0x04 << 2 ,
	"MULTISTEP_FILT":	0x08 << 3 ,
	"SHAFT":	0x10 << 4 ,
	"DIAG0_ERROR_ONLY_WITH_SD_MODE1":	0x20 << 5 ,
	"DIAG0_OTPW_ONLY_WITH_SD_MODE1":	0x40 << 6 ,
	"DIAG0_STALL":	0x80 << 7 ,
	"DIAG1_STALL":	0x0100 << 8 ,
	"DIAG1_INDEX":	0x0200 << 9 ,
	"DIAG1_ONSTATE":	0x0400 << 10 ,
	"DIAG1_STEPS_SKIPPED":	0x0800 << 11 ,
	"DIAG0_INT_PUSHPULL":	0x1000 << 12 ,
	"DIAG1_POSCOMP_PUSHPULL":	0x2000 << 13 ,
	"SMALL_HYSTERESIS":	0x4000 << 14 ,
	"STOP_ENABLE":	0x8000 << 15 ,
	"DIRECT_MODE":	0x010000 << 16 ,
	"TEST_MODE":	0x020000 << 17 ,
	"RECALIBRATE":	0x01 << 0 ,
	"FASTSTANDSTILL":	0x02 << 1 ,
	"EN_PWM_MODE":	0x04 << 2 ,
	"MULTISTEP_FILT":	0x08 << 3 ,
	"SHAFT":	0x10 << 4 ,
	"DIAG0_STEP":	0x80 << 7 ,
	"DIAG1_DIR":	0x0100 << 8 ,
	"DIAG0_INT_PUSHPULL":	0x1000 << 12 ,
	"DIAG1_POSCOMP_PUSHPULL":	0x2000 << 13 ,
	"SMALL_HYSTERESIS":	0x4000 << 14 ,
	"STOP_ENABLE":	0x8000 << 15 ,
	"DIRECT_MODE":	0x010000 << 16 ,
	"TEST_MODE":	0x020000 << 17
}
fields["GSTAT"] = {
	"RESET":	0x01 << 0 ,
	"DRV_ERR":	0x02 << 1 ,
	"UV_CP":	0x04 << 2
}
fields["IFCNT"] = {
	"IFCNT":	0xFF << 0
}
fields["SLAVECONF"] = {
	"SLAVEADDR":	0xFF << 0 ,
	"SENDDELAY":	0x0F00 << 8
}
fields["IOIN/OUTPUT"] = {
	"REFL_STEP":	0x01 << 0 ,
	"REFR_DIR":	0x02 << 1 ,
	"ENCB_DCEN_CFG4":	0x04 << 2 ,
	"ENCA_DCIN_CFG5":	0x08 << 3 ,
	"DRV_ENN_CFG6":	0x10 << 4 ,
	"ENC_N_DCO":	0x20 << 5 ,
	"SD_MODE":	0x40 << 6 ,
	"SWCOMP_IN":	0x80 << 7 ,
	"VERSION":	0xFF000000 << 24 ,
	"OUTPUT_PIN_POLARITY":	0x01 << 0
}
fields["X_COMPARE"] = {
	"X_COMPARE":	0xFFFFFFFF << 0
}
fields["OTP_PROG"] = {
	"OTPBIT":	0x07 << 0 ,
	"OTPBYTE":	0x30 << 4 ,
	"OTPMAGIC":	0xFF00 << 8
}
fields["OTP_READ"] = {
	"OTP_TBL":	0x80 << 7 ,
	"OTP_BBM":	0x40 << 6 ,
	"OTP_S2_LEVEL":	0x20 << 5 ,
	"OTP_FCLKTRIM":	0x1F << 0
}
fields["FACTORY_CONF"] = {
	"FCLKTRIM":	0x1F << 0
}
fields["SHORT_CONF"] = {
	"S2VS_LEVEL":	0x0F << 0 ,
	"S2GND_LEVEL":	0x0F00 << 8 ,
	"SHORTFILTER":	0x030000 << 16 ,
	"SHORTDELAY":	0x040000 << 18
}
fields["DRV_CONF"] = {
	"BBMTIME":	0x1F << 0 ,
	"BBMCLKS":	0x0F00 << 8 ,
	"OTSELECT":	0x030000 << 16 ,
	"DRVSTRENGTH":	0x0C0000 << 18 ,
	"FILT_ISENSE":	0x300000 << 20
}
fields["GLOBAL_SCALER"] = {
	"GLOBAL_SCALER":	0xFF << 0
}

fields["IHOLD_IRUN"] = {
	"IHOLD":	0x1F << 0 ,
	"IRUN":	0x1F00 << 8 ,
	"IHOLDDELAY":	0x0F0000 << 16
}
fields["TPOWERDOWN"] = {
	"TPOWERDOWN":	0xFF << 0
}
fields["TSTEP"] = {
	"TSTEP":	0x0FFFFF << 0
}
fields["TPWMTHRS"] = {
	"TPWMTHRS":	0x0FFFFF << 0
}
fields["TCOOLTHRS"] = {
	"TCOOLTHRS":	0x0FFFFF << 0
}
fields["THIGH"] = {
	"THIGH":	0x0FFFFF << 0
}
fields["RAMPMODE"] = {
	"RAMPMODE":	0x03 << 0
}
fields["XACTUAL"] = {
	"XACTUAL":	0xFFFFFFFF << 0
}
fields["VACTUAL"] = {
	"VACTUAL":	0xFFFFFF << 0
}
fields["VSTART"] = {
	"VSTART":	0x03FFFF << 0
}
fields["A1"] = {
	"A1":	0xFFFF << 0
}
fields["V1"] = {
	"V1_":	0x0FFFFF << 0
}
fields["AMAX"] = {
	"AMAX":	0xFFFF << 0
}
fields["VMAX"] = {
	"VMAX":	0x7FFFFF << 0
}
fields["DMAX"] = {
	"DMAX":	0xFFFF << 0
}
fields["D1"] = {
	"D1":	0xFFFF << 0
}
fields["VSTOP"] = {
	"VSTOP":	0x03FFFF << 0 
}
fields["TZEROWAIT"] = {
	"TZEROWAIT":	0xFFFF << 0 
}
fields["XTARGET"] = {
	"XTARGET":	0xFFFFFFFF << 0 
}
fields["VDCMIN"] = {
	"VDCMIN":	0x7FFFFF << 0 
}
fields["SW_MODE"] = {
	"STOP_L_ENABLE":	0x01 << 0 ,
	"STOP_R_ENABLE":	0x02 << 1 ,
	"POL_STOP_L":	0x04 << 2 ,
	"POL_STOP_R":	0x08 << 3 ,
	"SWAP_LR":	0x10 << 4 ,
	"LATCH_L_ACTIVE":	0x20 << 5 ,
	"LATCH_L_INACTIVE":	0x40 << 6 ,
	"LATCH_R_ACTIVE":	0x80 << 7 ,
	"LATCH_R_INACTIVE":	0x0100 << 8 ,
	"EN_LATCH_ENCODER":	0x0200 << 9 ,
	"SG_STOP":	0x0400 << 10 ,
	"EN_SOFTSTOP":	0x0800 << 11 
}
fields["RAMP_STAT"] = {
	"STATUS_STOP_L":	0x01 << 0 ,
	"STATUS_STOP_R":	0x02 << 1 ,
	"STATUS_LATCH_L":	0x04 << 2 ,
	"STATUS_LATCH_R":	0x08 << 3 ,
	"EVENT_STOP_L":	0x10 << 4 ,
	"EVENT_STOP_R":	0x20 << 5 ,
	"EVENT_STOP_SG":	0x40 << 6 ,
	"EVENT_POS_REACHED":	0x80 << 7 ,
	"VELOCITY_REACHED":	0x0100 << 8 ,
	"POSITION_REACHED":	0x0200 << 9 ,
	"VZERO":	0x0400 << 10 ,
	"T_ZEROWAIT_ACTIVE":	0x0800 << 11 ,
	"SECOND_MOVE":	0x1000 << 12 ,
	"STATUS_SG":	0x2000 << 13 
}
fields["XLATCH"] = {
	"XLATCH":	0xFFFFFFFF << 0 ,
}
fields["ENCMODE"] = {
	"POL_A":	0x01 << 0 ,
	"POL_B":	0x02 << 1 ,
	"POL_N":	0x04 << 2 ,
	"IGNORE_AB":	0x08 << 3 ,
	"CLR_CONT":	0x10 << 4 ,
	"CLR_ONCE":	0x20 << 5 ,
	"POS_EDGENEG_EDGE":	0xC0 << 6 ,
	"CLR_ENC_X":	0x0100 << 8 ,
	"LATCH_X_ACT":	0x0200 << 9 ,
	"ENC_SEL_DECIMAL":	0x0400 << 10 ,
}
fields["X_ENC"] = {
	"X_ENC":	0xFFFFFFFF << 0 ,
}
fields["ENC_CONST"] = {
	"INTEGER":	0xFFFF0000 << 16 ,
	"FRACTIONAL":	0xFFFF << 0 ,
}
fields["ENC_STATUS"] = {
	"N_EVENT":	0x01 << 0 ,
	"DEVIATION_WARN":	0x02 << 1 ,
}
fields["ENC_LATCH"] = {
	"ENC_LATCH":	0xFFFFFFFF << 0 ,
}
fields["ENC_DEVIATION"] = {
	"ENC_DEVIATION":	0x0FFFFF << 0 ,
}
fields["MSLUT[0]"] = {
	"OFS0":	0x01 << 0 ,
	"OFS1":	0x02 << 1 ,
	"OFS2":	0x04 << 2 ,
	"OFS3":	0x08 << 3 ,
	"OFS4":	0x10 << 4 ,
	"OFS5":	0x20 << 5 ,
	"OFS6":	0x40 << 6 ,
	"OFS7":	0x80 << 7 ,
	"OFS8":	0x0100 << 8 ,
	"OFS9":	0x0200 << 9 ,
	"OFS10":	0x0400 << 10 ,
	"OFS11":	0x0800 << 11 ,
	"OFS12":	0x1000 << 12 ,
	"OFS13":	0x2000 << 13 ,
	"OFS14":	0x4000 << 14 ,
	"OFS15":	0x8000 << 15 ,
	"OFS16":	0x010000 << 16 ,
	"OFS17":	0x020000 << 17 ,
	"OFS18":	0x040000 << 18 ,
	"OFS19":	0x080000 << 19 ,
	"OFS20":	0x100000 << 20 ,
	"OFS21":	0x200000 << 21 ,
	"OFS22":	0x400000 << 22 ,
	"OFS23":	0x800000 << 23 ,
	"OFS24":	0x01000000 << 24 ,
	"OFS25":	0x02000000 << 25 ,
	"OFS26":	0x04000000 << 26 ,
	"OFS27":	0x08000000 << 27 ,
	"OFS28":	0x10000000 << 28 ,
	"OFS29":	0x20000000 << 29 ,
	"OFS30":	0x40000000 << 30 ,
	"OFS31":	0x80000000 << 31 ,
}
fields["MSLUT[1]"] = {
	"OFS32":	0x01 << 0 ,
	"OFS33":	0x02 << 1 ,
	"OFS34":	0x04 << 2 ,
	"OFS35":	0x08 << 3 ,
	"OFS36":	0x10 << 4 ,
	"OFS37":	0x20 << 5 ,
	"OFS38":	0x40 << 6 ,
	"OFS39":	0x80 << 7 ,
	"OFS40":	0x0100 << 8 ,
	"OFS41":	0x0200 << 9 ,
	"OFS42":	0x0400 << 10 ,
	"OFS43":	0x0800 << 11 ,
	"OFS44":	0x1000 << 12 ,
	"OFS45":	0x2000 << 13 ,
	"OFS46":	0x4000 << 14 ,
	"OFS47":	0x8000 << 15 ,
	"OFS48":	0x010000 << 16 ,
	"OFS49":	0x020000 << 17 ,
	"OFS50":	0x040000 << 18 ,
	"OFS51":	0x080000 << 19 ,
	"OFS52":	0x100000 << 20 ,
	"OFS53":	0x200000 << 21 ,
	"OFS54":	0x400000 << 22 ,
	"OFS55":	0x800000 << 23 ,
	"OFS56":	0x01000000 << 24 ,
	"OFS57":	0x02000000 << 25 ,
	"OFS58":	0x04000000 << 26 ,
	"OFS59":	0x08000000 << 27 ,
	"OFS60":	0x10000000 << 28 ,
	"OFS61":	0x20000000 << 29 ,
	"OFS62":	0x40000000 << 30 ,
	"OFS63":	0x80000000 << 31 ,
}
fields["MSLUT[2]"] = {
	"OFS64":	0x01 << 0 ,
	"OFS65":	0x02 << 1 ,
	"OFS66":	0x04 << 2 ,
	"OFS67":	0x08 << 3 ,
	"OFS68":	0x10 << 4 ,
	"OFS69":	0x20 << 5 ,
	"OFS70":	0x40 << 6 ,
	"OFS71":	0x80 << 7 ,
	"OFS72":	0x0100 << 8 ,
	"OFS73":	0x0200 << 9 ,
	"OFS74":	0x0400 << 10 ,
	"OFS75":	0x0800 << 11 ,
	"OFS76":	0x1000 << 12 ,
	"OFS77":	0x2000 << 13 ,
	"OFS78":	0x4000 << 14 ,
	"OFS79":	0x8000 << 15 ,
	"OFS80":	0x010000 << 16 ,
	"OFS81":	0x020000 << 17 ,
	"OFS82":	0x040000 << 18 ,
	"OFS83":	0x080000 << 19 ,
	"OFS84":	0x100000 << 20 ,
	"OFS85":	0x200000 << 21 ,
	"OFS86":	0x400000 << 22 ,
	"OFS87":	0x800000 << 23 ,
	"OFS88":	0x01000000 << 24 ,
	"OFS89":	0x02000000 << 25 ,
	"OFS90":	0x04000000 << 26 ,
	"OFS91":	0x08000000 << 27 ,
	"OFS92":	0x10000000 << 28 ,
	"OFS93":	0x20000000 << 29 ,
	"OFS94":	0x40000000 << 30 ,
	"OFS95":	0x80000000 << 31 ,
}
fields["MSLUT[3]"] = {
	"OFS96":	0x01 << 0 ,
	"OFS97":	0x02 << 1 ,
	"OFS98":	0x04 << 2 ,
	"OFS99":	0x08 << 3 ,
	"OFS100":	0x10 << 4 ,
	"OFS101":	0x20 << 5 ,
	"OFS102":	0x40 << 6 ,
	"OFS103":	0x80 << 7 ,
	"OFS104":	0x0100 << 8 ,
	"OFS105":	0x0200 << 9 ,
	"OFS106":	0x0400 << 10 ,
	"OFS107":	0x0800 << 11 ,
	"OFS108":	0x1000 << 12 ,
	"OFS109":	0x2000 << 13 ,
	"OFS110":	0x4000 << 14 ,
	"OFS111":	0x8000 << 15 ,
	"OFS112":	0x010000 << 16 ,
	"OFS113":	0x020000 << 17 ,
	"OFS114":	0x040000 << 18 ,
	"OFS115":	0x080000 << 19 ,
	"OFS116":	0x100000 << 20 ,
	"OFS117":	0x200000 << 21 ,
	"OFS118":	0x400000 << 22 ,
	"OFS119":	0x800000 << 23 ,
	"OFS120":	0x01000000 << 24 ,
	"OFS121":	0x02000000 << 25 ,
	"OFS122":	0x04000000 << 26 ,
	"OFS123":	0x08000000 << 27 ,
	"OFS124":	0x10000000 << 28 ,
	"OFS125":	0x20000000 << 29 ,
	"OFS126":	0x40000000 << 30 ,
	"OFS127":	0x80000000 << 31 ,
}
fields["MSLUT[4]"] = {
	"OFS128":	0x01 << 0 ,
	"OFS129":	0x02 << 1 ,
	"OFS130":	0x04 << 2 ,
	"OFS131":	0x08 << 3 ,
	"OFS132":	0x10 << 4 ,
	"OFS133":	0x20 << 5 ,
	"OFS134":	0x40 << 6 ,
	"OFS135":	0x80 << 7 ,
	"OFS136":	0x0100 << 8 ,
	"OFS137":	0x0200 << 9 ,
	"OFS138":	0x0400 << 10 ,
	"OFS139":	0x0800 << 11 ,
	"OFS140":	0x1000 << 12 ,
	"OFS141":	0x2000 << 13 ,
	"OFS142":	0x4000 << 14 ,
	"OFS143":	0x8000 << 15 ,
	"OFS144":	0x010000 << 16 ,
	"OFS145":	0x020000 << 17 ,
	"OFS146":	0x040000 << 18 ,
	"OFS147":	0x080000 << 19 ,
	"OFS148":	0x100000 << 20 ,
	"OFS149":	0x200000 << 21 ,
	"OFS150":	0x400000 << 22 ,
	"OFS151":	0x800000 << 23 ,
	"OFS152":	0x01000000 << 24 ,
	"OFS153":	0x02000000 << 25 ,
	"OFS154":	0x04000000 << 26 ,
	"OFS155":	0x08000000 << 27 ,
	"OFS156":	0x10000000 << 28 ,
	"OFS157":	0x20000000 << 29 ,
	"OFS158":	0x40000000 << 30 ,
	"OFS159":	0x80000000 << 31 ,
}
fields["MSLUT[5]"] = {
	"OFS160":	0x01 << 0 ,
	"OFS161":	0x02 << 1 ,
	"OFS162":	0x04 << 2 ,
	"OFS163":	0x08 << 3 ,
	"OFS164":	0x10 << 4 ,
	"OFS165":	0x20 << 5 ,
	"OFS166":	0x40 << 6 ,
	"OFS167":	0x80 << 7 ,
	"OFS168":	0x0100 << 8 ,
	"OFS169":	0x0200 << 9 ,
	"OFS170":	0x0400 << 10 ,
	"OFS171":	0x0800 << 11 ,
	"OFS172":	0x1000 << 12 ,
	"OFS173":	0x2000 << 13 ,
	"OFS174":	0x4000 << 14 ,
	"OFS175":	0x8000 << 15 ,
	"OFS176":	0x010000 << 16 ,
	"OFS177":	0x020000 << 17 ,
	"OFS178":	0x040000 << 18 ,
	"OFS179":	0x080000 << 19 ,
	"OFS180":	0x100000 << 20 ,
	"OFS181":	0x200000 << 21 ,
	"OFS182":	0x400000 << 22 ,
	"OFS183":	0x800000 << 23 ,
	"OFS184":	0x01000000 << 24 ,
	"OFS185":	0x02000000 << 25 ,
	"OFS186":	0x04000000 << 26 ,
	"OFS187":	0x08000000 << 27 ,
	"OFS188":	0x10000000 << 28 ,
	"OFS189":	0x20000000 << 29 ,
	"OFS190":	0x40000000 << 30 ,
	"OFS191":	0x80000000 << 31 ,
}
fields["MSLUT[6]"] = {
	"OFS192":	0x01 << 0 ,
	"OFS193":	0x02 << 1 ,
	"OFS194":	0x04 << 2 ,
	"OFS195":	0x08 << 3 ,
	"OFS196":	0x10 << 4 ,
	"OFS197":	0x20 << 5 ,
	"OFS198":	0x40 << 6 ,
	"OFS199":	0x80 << 7 ,
	"OFS200":	0x0100 << 8 ,
	"OFS201":	0x0200 << 9 ,
	"OFS202":	0x0400 << 10 ,
	"OFS203":	0x0800 << 11 ,
	"OFS204":	0x1000 << 12 ,
	"OFS205":	0x2000 << 13 ,
	"OFS206":	0x4000 << 14 ,
	"OFS207":	0x8000 << 15 ,
	"OFS208":	0x010000 << 16 ,
	"OFS209":	0x020000 << 17 ,
	"OFS210":	0x040000 << 18 ,
	"OFS211":	0x080000 << 19 ,
	"OFS212":	0x100000 << 20 ,
	"OFS213":	0x200000 << 21 ,
	"OFS214":	0x400000 << 22 ,
	"OFS215":	0x800000 << 23 ,
	"OFS216":	0x01000000 << 24 ,
	"OFS217":	0x02000000 << 25 ,
	"OFS218":	0x04000000 << 26 ,
	"OFS219":	0x08000000 << 27 ,
	"OFS220":	0x10000000 << 28 ,
	"OFS221":	0x20000000 << 29 ,
	"OFS222":	0x40000000 << 30 ,
	"OFS223":	0x80000000 << 31 ,
}
fields["MSLUT[7]"] = {
	"OFS224":	0x01 << 0 ,
	"OFS225":	0x02 << 1 ,
	"OFS226":	0x04 << 2 ,
	"OFS227":	0x08 << 3 ,
	"OFS228":	0x10 << 4 ,
	"OFS229":	0x20 << 5 ,
	"OFS230":	0x40 << 6 ,
	"OFS231":	0x80 << 7 ,
	"OFS232":	0x0100 << 8 ,
	"OFS233":	0x0200 << 9 ,
	"OFS234":	0x0400 << 10 ,
	"OFS235":	0x0800 << 11 ,
	"OFS236":	0x1000 << 12 ,
	"OFS237":	0x2000 << 13 ,
	"OFS238":	0x4000 << 14 ,
	"OFS239":	0x8000 << 15 ,
	"OFS240":	0x010000 << 16 ,
	"OFS241":	0x020000 << 17 ,
	"OFS242":	0x040000 << 18 ,
	"OFS243":	0x080000 << 19 ,
	"OFS244":	0x100000 << 20 ,
	"OFS245":	0x200000 << 21 ,
	"OFS246":	0x400000 << 22 ,
	"OFS247":	0x800000 << 23 ,
	"OFS248":	0x01000000 << 24 ,
	"OFS249":	0x02000000 << 25 ,
	"OFS250":	0x04000000 << 26 ,
	"OFS251":	0x08000000 << 27 ,
	"OFS252":	0x10000000 << 28 ,
	"OFS253":	0x20000000 << 29 ,
	"OFS254":	0x40000000 << 30 ,
	"OFS255":	0x80000000 << 31 ,
}
fields["MSLUTSEL"] = {
	"W0":	0x03 << 0 ,
	"W1":	0x0C << 2 ,
	"W2":	0x30 << 4 ,
	"W3":	0xC0 << 6 ,
	"X1":	0xFF00 << 8 ,
	"X2":	0xFF0000 << 16 ,
	"X3":	0xFF000000 << 24 ,
}
fields["MSLUTSTART"] = {
	"START_SIN":	0xFF << 0 ,
	"START_SIN90":	0xFF0000 << 16 ,
}
fields["MSCNT"] = {
	"MSCNT":	0x03FF << 0 ,
}
fields["MSCURACT"] = {
	"CUR_A":	0x01FF << 0 ,
	"CUR_B":	0x01FF0000 << 16 ,
}
fields["CHOPCONF"] = {
	"TOFF":	0x0F << 0 ,
	"TFD_ALL":	0x70 << 4 ,
	"OFFSET":	0x0780 << 7 ,
	"TFD_3":	0x0800 << 11 ,
	"DISFDCC":	0x1000 << 12 ,
	"CHM":	0x4000 << 14 ,
	"TBL":	0x018000 << 15 ,
	"VHIGHFS":	0x040000 << 18 ,
	"VHIGHCHM":	0x080000 << 19 ,
	"TPFD":	0xF00000 << 20 ,
	"MRES":	0x0F000000 << 24 ,
	"INTPOL":	0x10000000 << 28 ,
	"DEDGE":	0x20000000 << 29 ,
	"DISS2G":	0x40000000 << 30 ,
	"DISS2VS":	0x80000000 << 31 ,
	"TOFF":	0x0F << 0 ,
	"TFD_ALL":	0x70 << 4 ,
	"OFFSET":	0x0780 << 7 ,
	"TFD_3":	0x0800 << 11 ,
	"DISFDCC":	0x1000 << 12 ,
	"RNDTF":	0x2000 << 13 ,
	"CHM":	0x4000 << 14 ,
	"TBL":	0x018000 << 15 ,
	"VSENSE":	0x020000 << 17 ,
	"VHIGHFS":	0x040000 << 18 ,
	"VHIGHCHM":	0x080000 << 19 ,
	"TPFD":	0xF00000 << 20 ,
	"MRES":	0x0F000000 << 24 ,
	"INTPOL":	0x10000000 << 28 ,
	"DEDGE":	0x20000000 << 29 ,
	"DISS2G":	0x40000000 << 30 ,
	"DISS2VS":	0x80000000 << 31 ,
	"TOFF":	0x0F << 0 ,
	"HSTRT":	0x70 << 4 ,
	"HEND":	0x0780 << 7 ,
	"CHM":	0x4000 << 14 ,
	"TBL":	0x018000 << 15 ,
	"VHIGHFS":	0x040000 << 18 ,
	"VHIGHCHM":	0x080000 << 19 ,
	"TPFD":	0xF00000 << 20 ,
	"MRES":	0x0F000000 << 24 ,
	"INTPOL":	0x10000000 << 28 ,
	"DEDGE":	0x20000000 << 29 ,
	"DISS2G":	0x40000000 << 30 ,
	"DISS2VS":	0x80000000 << 31 ,
}
fields["COOLCONF"] = {
	"SEMIN":	0x0F << 0 ,
	"SEUP":	0x60 << 5 ,
	"SEMAX":	0x0F00 << 8 ,
	"SEDN":	0x6000 << 13 ,
	"SEIMIN":	0x8000 << 15 ,
	"SGT":	0x7F0000 << 16 ,
	"SFILT":	0x01000000 << 24 ,
}
fields["DCCTRL"] = {
	"DC_TIME":	0x03FF << 0 ,
	"DC_SG":	0xFF0000 << 16 ,
}
fields["DRV_STATUS"] = {
	"SG_RESULT":	0x03FF << 0 ,
	"FSACTIVE":	0x8000 << 15 ,
	"CS_ACTUAL":	0x1F0000 << 16 ,
	"STALLGUARD":	0x01000000 << 24 ,
	"OT":	0x02000000 << 25 ,
	"OTPW":	0x04000000 << 26 ,
	"S2GA":	0x08000000 << 27 ,
	"S2GB":	0x10000000 << 28 ,
	"OLA":	0x20000000 << 29 ,
	"OLB":	0x40000000 << 30 ,
	"STST":	0x80000000 << 31 ,
}
fields["PWMCONF"] = {
	"PWM_OFS":	0xFF << 0 ,
	"PWM_GRAD":	0xFF00 << 8 ,
	"PWM_FREQ":	0x030000 << 16 ,
	"PWM_AUTOSCALE":	0x040000 << 18 ,
	"PWM_AUTOGRAD":	0x080000 << 19 ,
	"FREEWHEEL":	0x300000 << 20 ,
	"PWM_REG":	0x0F000000 << 24 ,
	"PWM_LIM":	0xF0000000 << 28
}
fields["PWM_SCALE"] = {
	"PWM_SCALE_SUM":	0xFF << 0 ,
	"PWM_SCALE_AUTO":	0x01FF0000 << 16
}
fields["PWM_AUTO"] = {
	"PWM_OFS_AUTO":	0xFF << 0 ,
	"PWM_GRAD_AUTO":	0xFF0000 << 16
}
fields["LOST_STEPS"] = {
	"LOST_STEPS":	0x0FFFFF << 0
}


#

FieldFormatters = {
    "MRES": (lambda v: "%d(%dusteps)" % (v, 0x100 >> v)),
    "DEDGE": (lambda v:
        "1(Both Edges Active)" if v else "0(Only Rising Edge active)"),
    "INTPOL": (lambda v: "1(On)" if v else "0(Off)"),
    "TOFF": (lambda v: ("%d" % v) if v else "0(Driver Disabled!)"),
    "CHM": (lambda v: "1(constant toff)" if v else "0(spreadCycle)"),
    "SGT": (lambda v: "%d" % (v)),
    "SFILT": (lambda v: "1(Filtered mode)" if v else "0(Standard mode)"),
    "VSENSE": (lambda v: "%d(%dmV)" % (v, 165 if v else 305)),
    "SDOFF": (lambda v: "1(Step/Dir disabled" if v else "0(Step/dir enabled)"),
    "DISS2G": (lambda v: "%d(Short to GND protection %s)" % (v,
                                          "disabled" if v else "enabled")),
    "MSTEP": (lambda v: "%d(%d, OA1 %s OA2)" % (v, v & 0xff,
                                                "<=" if v & 0x100 else "=>")),
    "SG": (lambda v: "%d(%s)" % (v, "Stall!" if v else "No Stall!")),
    "OT": (lambda v: "1(Overtemp shutdown!)" if v else ""),
    "OTPW": (lambda v: "1(Overtemp warning!)" if v else ""),
    "S2GA": (lambda v: "1(Short to GND Coil A!)" if v else ""),
    "S2GB": (lambda v: "1(Short to GND Coil B!)" if v else ""),
    "OLA": (lambda v: "1(Open Load Coil A at slow speed!)" if v else ""),
    "OLB": (lambda v: "1(Open Load Coil B at slow speed!)" if v else ""),
    "STST": (lambda v: "1(Standstill detected!)" if v else ""),
    "I_scale_analog":   (lambda v: "1(ExtVREF)" if v else ""),
    "shaft":            (lambda v: "1(Reverse)" if v else ""),
    "drv_err":          (lambda v: "1(ErrorShutdown!)" if v else ""),
    "uv_cp":            (lambda v: "1(Undervoltage!)" if v else ""),
    "VERSION":          (lambda v: "%#x" % v),
    "CUR_A":            (lambda v: decode_signed_int(v, 9)),
    "CUR_B":            (lambda v: decode_signed_int(v, 9)),
    "MRES":             (lambda v: "%d(%dusteps)" % (v, 0x100 >> v)),
    "otpw":             (lambda v: "1(OvertempWarning!)" if v else ""),
    "ot":               (lambda v: "1(OvertempError!)" if v else ""),
    "s2ga":             (lambda v: "1(ShortToGND_A!)" if v else ""),
    "s2gb":             (lambda v: "1(ShortToGND_B!)" if v else ""),
    "ola":              (lambda v: "1(OpenLoad_A!)" if v else ""),
    "olb":              (lambda v: "1(OpenLoad_B!)" if v else ""),
    "sgt":              (lambda v: decode_signed_int(v, 7))
}

#######################################################################################

class TMC5160:

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.spi = bus.MCU_SPI_from_config(config, 3, default_speed=4000000)
        self.gcode = self.printer.lookup_object("gcode")
        #
        self.gcode.register_mux_command("DUMP_TMC", "STEPPER", self.name, self.cmd_DUMP_TMC, desc=self.cmd_DUMP_TMC_help)
        #
        # Setup basic register values
        self.regs = collections.OrderedDict()
        self.fields = tmc2130.FieldHelper(fields, FieldFormatters, self.regs)
        vsense, irun, ihold, self.sense_resistor = tmc2130.get_config_current(config)
        #self.fields.set_field("vsense", vsense)
        self.fields.set_field("IHOLD", ihold)
        self.fields.set_field("IRUN", irun)
        mres, en_pwm, thresh = tmc2130.get_config_stealthchop(config, TMC_FREQUENCY)
        self.fields.set_field("MRES", mres)
        self.fields.set_field("en_pwm_mode", en_pwm)
        self.fields.set_field("TPWMTHRS", thresh)
        #
        #
        # Allow other registers to be set from the config
        set_config_field = self.fields.set_config_field
        set_config_field(config, "toff", 3)
        set_config_field(config, "hstrt", 4)
        set_config_field(config, "hend", 1)
        set_config_field(config, "TBL", 2)
        set_config_field(config, "intpol", True, "interpolate")
        set_config_field(config, "IHOLDDELAY", 6)
        set_config_field(config, "TPOWERDOWN", 10)
        set_config_field(config, "PWM_OFS", 128) #
        set_config_field(config, "PWM_GRAD", 4) #
        set_config_field(config, "pwm_freq", 1)
        set_config_field(config, "pwm_autoscale", True)
        sgt = config.getint('driver_SGT', 0, minval=-64, maxval=63) & 0x7f
        self.fields.set_field("sgt", sgt)
        set_config_field(config, "test_mode", 0)
        set_config_field(config, "direct_mode", 0)
        

        #
        self._init_registers()
    def _init_registers(self, min_clock=0):
        # Send registers
        logging.error("======== 5160 ============")
        for reg_name, val in self.regs.items():
            logging.error( reg_name )
            logging.info( val )
            self.set_register(reg_name, val, min_clock)

    cmd_DUMP_TMC_help = "Read and display TMC stepper driver registers"
    def cmd_DUMP_TMC(self, params):
        logging.info("DUMP_TMC %s", self.name)
        for reg_ in registers.keys():
            repl_ = self.get_register(reg_)
            logging.info( reg_ + "\t" + hex(repl_) )
        logging.info("=======================")

        for reg_name, val in self.regs.items():
            try:
                logging.error( str(reg_name) + " - " + str(val) )
                logging.error(self.fields.pretty_format(reg_name, val) + "\n")
            except Exception as e:
                pass

    def get_register(self, reg_name):
        reg = registers[reg_name]
        self.spi.spi_send([reg, 0x00, 0x00, 0x00, 0x00])
        params = self.spi.spi_transfer([reg, 0x00, 0x00, 0x00, 0x00])
        pr = bytearray(params['response'])
        return (pr[1] << 24) | (pr[2] << 16) | (pr[3] << 8) | pr[4]

    def set_register(self, reg_name, val, min_clock = 0):
        reg = registers[reg_name]
        data = [(reg | 0x80) & 0xff, (val >> 24) & 0xff, (val >> 16) & 0xff,
                (val >> 8) & 0xff, val & 0xff]
        self.spi.spi_send(data, min_clock)


def load_config_prefix(config):
    return TMC5160(config)
