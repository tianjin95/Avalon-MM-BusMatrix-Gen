#   Avalon-MM BUS Matrix
#   Read Fixed-Latency for 1 cycle
#   Write Fixed-Latency for none
#   No burst support

import math

#   Global Config



# The Number of Slave  
NumSlave = 6

# The Number of Master
NumMaster = 8

# Width of Address
WidthAddr = 64

# Width of Data
WidthData = 1024

# Width of ByteEnable
WidthByteEn = math.ceil(WidthData/8)

# Width of MasterNum
WidthNumMst = math.ceil(math.log(NumMaster,2))

# Width of SlaveNum
WidthNumSlv = math.ceil(math.log(NumSlave,2))

# Size of Slave Address
SizeSlvAddr = 9

# Connection between Master and Slave
Connection = [ [1,1,0,0,0,0], [0,0,1,0,0,0], [0,0,0,1,0,0], [0,0,0,0,1,0], [0,0,0,0,0,1], [0,1,1,1,1,1], [0,1,1,1,1,1], [1,1,1,1,1,1] ]

# Output Path
OutputPath = "./verilog/"



#   Generate Decoder File


# Open File
fdec = open(OutputPath + "AvalonBusMatrixDecoder.v",'w')

# Write Module Name
fdec.write("module AvalonBusMatrixDecoder #(\n")
# Write Parameter List
for i in range(0,NumSlave):
    fdec.write("\tparameter\t\t\t\t\tPort"+str(i)+"En\t=\t1'b1,\n") 
fdec.write("\tparameter\t\t\t\t\tMstID\t=\t"+str(WidthNumMst)+"'h0\n")
# Write )(
fdec.write(")\t(\n")

# System Signal List
DecSysSigList = ["clk","rstn"]
DecMstSigList = ["Addr","RdEn","WrEn"]
DecSlvSigList = ["RdData","WaitReq","PortSel"]

# Write Port List
# Write System Signal
fdec.write("\t//\tSystem Signals\n")
for i in DecSysSigList:
    fdec.write("\tinput\twire\t\t\t\t"+i+",\n")
# Write Master Signal
fdec.write("\n\t//\tMaster Input Signals\n")
fdec.write("\tinput\twire\t["+str(WidthAddr-1)+":0]\t\tAddr_i,\n")
fdec.write("\tinput\twire\t\t\t\tRdEn_i,\n")
fdec.write("\tinput\twire\t\t\t\tWrEn_i,\n")
# Write Slave Signal
for i in range(0,NumSlave):
    fdec.write("\n\t//\tSlave "+str(i)+" Input Signals\n")
    fdec.write("\tinput\twire\t["+str(WidthData-1)+":0]\tRdData"+str(i)+"_i,\n")
    fdec.write("\tinput\twire\t\t\t\tWaitReq"+str(i)+"_i,\n")
    fdec.write("\tinput\twire\t["+str(WidthNumMst-1)+":0]\t\tPortSel"+str(i)+"_i,\n")
# Write Request Signal
fdec.write("\n\t//\tRequest Signals\n")
for i in range(0,NumSlave):
    fdec.write("\toutput\twire\t\t\t\tReq"+str(i)+"_o,\n")
# Write Master Side Output Signal
fdec.write("\n\t//\tMaster Output Signals\n")
fdec.write("\toutput\twire\t["+str(WidthData-1)+":0]\tRdDataDec_o,\n")
fdec.write("\toutput\twire\t\t\t\tWaitReq_o\n")
# Write );
fdec.write(");\n\n")

# Write Decoder Logic
for i in range(0,NumSlave):
    fdec.write("assign\tReq"+str(i)+"_o\t=\t(Addr_i["+str(SizeSlvAddr+WidthNumSlv-1)+":"+str(SizeSlvAddr)+"]\t==\t"+str(WidthNumSlv)+"'h"+str(i)+")\t&\tPort"+str(i)+"En\t&\t(RdEn_i\t|\tWrEn_i);\n")

# Write Read Sel DFF
fdec.write("\nreg\t["+str(NumSlave-1)+":0]\tSel;\n\n")
fdec.write("always@(posedge clk or negedge rstn\n")
fdec.write("\tif(~rstn)\n")
fdec.write("\t\tSel\t<=\t"+str(NumSlave)+"'b0;\n")
fdec.write("\telse if(~WaitReq_o)\n")
fdec.write("\t\tSel\t<=\t{")
for i in range(0,NumSlave):
    fdec.write("Req"+str(i)+"_o")
    if(i < NumSlave-1):
        fdec.write(", ")
    else:
        fdec.write("};\n\n")

# Write Mux of RdData
fdec.write("assign\tRdDataDec_o\t=\t")
for i in range(0,NumSlave):
    if(i == 0):
        fdec.write("({"+str(WidthData)+"{Sel["+str(i)+"]}}\t&\tRdData"+str(NumSlave-1-i)+"_i)\t|\n")
    else:
        fdec.write("\t\t\t\t\t\t({"+str(WidthData)+"{Sel["+str(i)+"]}}\t&\tRdData"+str(NumSlave-1-i)+"_i)\t")
        if(i < NumSlave-1):
            fdec.write("|\n")
        else:
            fdec.write(";\n\n")

# Write Mux of WaitReq
fdec.write("assign\tWaitReq_o\t=\t")
for i in range(0,NumSlave):
    if(i == 0):
        fdec.write("(Req"+str(i)+"_o\t&\t((PortSel"+str(i)+"_i\t!=\tMstID)\t|\tWaitReq"+str(i)+"_i))\t|\n")
    else:
        fdec.write("\t\t\t\t\t\t(Req"+str(i)+"_o\t&\t((PortSel"+str(i)+"_i\t!=\tMstID)\t|\tWaitReq"+str(i)+"_i))\t")
        if(i < NumSlave-1):
            fdec.write("|\n")
        else:
            fdec.write(";\n\n")

# Write endmodule
fdec.write("endmodule\n")

# Close File
fdec.close



#   Generate Arbiter File


# Open File
farb = open(OutputPath + "AvalonBusMatrixArbiter.v",'w')

# Write Module Name
farb.write("module AvalonBusMatrixArbiter (\n")

# System Signal List
ArbSysSigList = ["clk","rstn"]

# Write Port List
# Write System Signal
farb.write("\t//\tSystem Signals\n")
for i in ArbSysSigList:
    farb.write("\tinput\twire\t\t\t\t"+i+",\n")
# Write Request Signals
farb.write("\n\t//\tRequest Signals\n")
for i in range(0,NumMaster):
    farb.write("\tinput\twire\t\t\t\tReq"+str(i)+"_i,\n")
# Write Arbitration Signals
farb.write("\n\t//\tArbitration Signals\n")
farb.write("\toutput\twire\t["+str(WidthNumMst-1)+":0]\t\tPortSel_o,\n")
farb.write("\toutput\twire\t\t\t\tPortNoSel_o\n")
farb.write(");\n\n")

# Write NoPort Logic
farb.write("assign\tPortNoSel_o\t=\t")
for i in range(0,NumMaster):
    if(i == 0):
        farb.write("~Req"+str(i)+"_i\t&\n")
    else:
        farb.write("\t\t\t\t\t\t~Req"+str(i)+"_i\t")
        if(i < NumMaster-1):
            farb.write("&\n")
        else:
            farb.write(";\n\n")

# Write PortSel Logic
farb.write("assign\tPortSel_o\t=\t")
for i in range(0,NumMaster):
    if(i == 0):
        farb.write("({"+str(WidthNumMst)+"{Req"+str(i)+"_i}}\t&\t"+str(WidthNumMst)+"'h"+str(i)+")\t|\n")
    else:
        farb.write("\t\t\t\t\t\t({"+str(WidthNumMst)+"{Req"+str(i)+"_i}}\t&\t"+str(WidthNumMst)+"'h"+str(i)+")\t")
        if(i < NumMaster-1):
            farb.write("|\n")
        else:
            farb.write(";\n\n")

# Write endmodule
farb.write("endmodule\n")

# Close File
farb.close



#   Generate Matrix File


# Open File
fmtx = open(OutputPath + "AvalonBusMatrix.v",'w')

# Write Module Name
fmtx.write("module AvalonBusMatrix (\n")

# System Signal List
MtxSysSigList = ["clk","rstn"]

# Write Port List
# Write System Signal
fmtx.write("\t//\tSystem Signals\n")
for i in MtxSysSigList:
    fmtx.write("\tinput\twire\t\t\t\t"+i+",\n")

# BUS Input Port List
MtxBusInList = ["Addr","ByteEn","RdEn","WrEn","WrData"]
# BUS Output Port List
MtxBusOutList = ["RdData","WaitReq"]

# Write Master Side Signals
for i in range(0,NumMaster):
    fmtx.write("\n\t//\tMaster "+str(i)+" Signals\n")
    # Write Master Input Signals
    for j in MtxBusInList:
        fmtx.write("\tinput\twire\t")
        if(j == "Addr_i"):
            fmtx.write("["+str(WidthAddr-1)+":0]\t")
        elif(j == "ByteEn"):
            fmtx.write("["+str(WidthByteEn-1)+":0]\t\t")
        elif(j == "WrData"):
            fmtx.write("["+str(WidthData-1)+":0]\t")
        else:
            fmtx.write("\t\t\t")
        fmtx.write("Master"+str(i)+j+"_i,\n")
    # Write Master Output Signals
    for j in MtxBusOutList:
        fmtx.write("\toutput\twire\t")
        if(j == "RdData"):
            fmtx.write("["+str(WidthData-1)+":0]\t")
        else:
            fmtx.write("\t\t\t")
        fmtx.write("Master"+str(i)+j+"_o,\n")

# Write Slave Side Signals
for i in range(0,NumSlave):
    fmtx.write("\n\t//\tSlave "+str(i)+" Signals\n")
    # Write Slave Output Signals
    for j in MtxBusInList:
        fmtx.write("\toutput\twire\t")
        if(j == "Addr_i"):
            fmtx.write("["+str(WidthAddr-1)+":0]\t")
        elif(j == "ByteEn"):
            fmtx.write("["+str(WidthByteEn-1)+":0]\t\t")
        elif(j == "WrData"):
            fmtx.write("["+str(WidthData-1)+":0]\t")
        else:
            fmtx.write("\t\t\t")
        fmtx.write("Slave"+str(i)+j+"_o,\n")
    # Write Slave Input Signals
    for j in MtxBusOutList:
        fmtx.write("\tinput\twire\t")
        if(j == "RdData"):
            fmtx.write("["+str(WidthData-1)+":0]\t")
        else:
            fmtx.write("\t\t\t")
        if((i == NumSlave-1) and (j == "WaitReq")):
            fmtx.write("Slave"+str(i)+j+"_i\n")
        else:
            fmtx.write("Slave"+str(i)+j+"_i,\n")
# Write );
fmtx.write(");\n\n")

# Write InputStage
# Write Wire Declar

for i in range(0,NumMaster):
    fmtx.write("wire\t")
    for j in range(0,NumSlave):
        fmtx.write("Master"+str(i)+"Req"+str(j))
        if(j == NumSlave-1):
            fmtx.write(";\n")
        else:
            fmtx.write(", ")

fmtx.write("\n")

for i in range(0,NumSlave):
    fmtx.write("wire\t["+str(WidthNumSlv-1)+":0]\tSlave"+str(i)+"PortSel;\n")

# Inst Decoder
for i in range(0,NumMaster):
    fmtx.write("\n//\tDecoder\t"+str(i)+"\n")
    fmtx.write("AvalonBusMatrixDecoder #(\n")
    for j in range(0,NumSlave):
        fmtx.write("\t.Port"+str(j)+"En\t\t\t\t("+str(Connection[i][j])+"),\n")
    fmtx.write("\t.MstID\t\t\t\t\t("+str(WidthNumMst)+"'h"+str(i)+")\n")
    fmtx.write(")\tDec"+str(i)+"\t(\n")
    for j in DecSysSigList:
        fmtx.write("\t."+j+"\t\t\t\t\t"+"("+j+"),\n")
    for j in DecMstSigList:
        fmtx.write("\t."+j+"_i\t\t\t\t\t"+"(Master"+str(i)+j+"_i),\n")
    for j in range(0,NumSlave):
        for k in DecSlvSigList:
            fmtx.write("\t."+k+str(j)+"_i\t\t\t\t"+"(Slave"+str(j)+k+"_i),\n")
    for j in range(0,NumSlave):
        fmtx.write("\t.Req"+str(j)+"_o\t\t\t\t\t"+"(Master"+str(i)+"Req"+str(j)+"),\n")
    fmtx.write("\t.RdDataDec_o\t\t\t(Master"+str(i)+"RdData_o),\n")
    fmtx.write("\t.WaitReq_o\t\t\t\t(Master"+str(i)+"WaitReq_o)\n")
    fmtx.write(");\n")

# Inst Arbiter
for i in range(0,NumSlave):
    fmtx.write("\n//\tArbiter\t"+str(i)+"\n")
    fmtx.write("AvalonBusMatrixArbiter\tArbiter"+str(i)+"(\n")
    for j in ArbSysSigList:
        fmtx.write("\t."+j+"\t\t\t\t\t"+"("+j+"),\n")
    for j in range(0,NumMaster):
        fmtx.write("\t.Req"+str(j)+"_i\t\t\t\t\t(Master"+str(j)+"Req"+str(i)+"),\n")
    fmtx.write("\t.PortSel_o\t\t\t\t(Slave"+str(i)+"PortSel),\n")
    fmtx.write("\t.PortNoSel_o\t\t\t(Slave"+str(i)+"PortNoSel)\n")
    fmtx.write(");\n")

# Write Slave Addr Mux
for i in MtxBusInList:
    for j in range(0,NumSlave):
        fmtx.write("assign\tSlave"+str(j)+i+"_o\t=\t(")
        if(i == "Addr"):
            fmtx.write("({"+str(WidthAddr)+"{Slave"+str(j)+"PortNoSel}})\t&\t(\n")
            for k in range(0,NumMaster):
                fmtx.write("\t\t\t\t\t\t\t({"+str(WidthAddr)+"{Slave"+str(j)+"PortSel\t==\t"+str(WidthNumMst)+"'h"+str(k)+"}}\t&\tMaster"+str(k)+i+"_i\t")
                if(k == NumMaster-1):
                    fmtx.write(");\n\n")
                else:
                    fmtx.write("|\n")
        elif(i == "ByteEn"):
            fmtx.write("({"+str(WidthByteEn)+"{Slave"+str(j)+"PortNoSel}})\t&\t(\n")
            for k in range(0,NumMaster):
                fmtx.write("\t\t\t\t\t\t\t({"+str(WidthByteEn)+"{Slave"+str(j)+"PortSel\t==\t"+str(WidthNumMst)+"'h"+str(k)+"}}\t&\tMaster"+str(k)+i+"_i\t")
                if(k == NumMaster-1):
                    fmtx.write(");\n\n")
                else:
                    fmtx.write("|\n")
        elif(i == "WrData"):
            fmtx.write("({"+str(WidthData)+"{Slave"+str(j)+"PortNoSel}})\t&\t(\n")
            for k in range(0,NumMaster):
                fmtx.write("\t\t\t\t\t\t\t({"+str(WidthData)+"{Slave"+str(j)+"PortSel\t==\t"+str(WidthNumMst)+"'h"+str(k)+"}}\t&\tMaster"+str(k)+i+"_i\t")
                if(k == NumMaster-1):
                    fmtx.write(");\n\n")
                else:
                    fmtx.write("|\n")
        else:
            fmtx.write("(Slave"+str(j)+"PortNoSel))\t&\t(\n")
            for k in range(0,NumMaster):
                fmtx.write("\t\t\t\t\t\t\t((Slave"+str(j)+"PortSel\t==\t"+str(WidthNumMst)+"'h"+str(k)+")\t&\tMaster"+str(k)+i+"_i\t")
                if(k == NumMaster-1):
                    fmtx.write(");\n\n")
                else:
                    fmtx.write("|\n")
fmtx.write("endmodule\n")
fmtx.close
    