# Tom Anderson
# vdiv_filter.jl
# MIT License
# 10/30/2016
# Demo program to show the frequency response of an 
# RC lowpass filter and an RLC lowpass filter

include("/Users/toma/tools/julia/rc_graph.jl")

fstart = 1
fstop = 10meg
npts = 2810
freq = logsweep(fstart, fstop, npts)

# RC lowpass filter
# R=100 Ohms, C= 0.01uF
filt1 = db(vdiv(zr(100,freq), zc(.01u,freq)))

# RLC lowpass filter with peaking. 
# R=100 Ohms, L=1mH, c=0.01uF
filt2 = db(vdiv(zr(100,freq) + zl(1m,freq), zc(.01u,freq)))

plt1 = FramedPlot()
setattr(plt1, "xlog", true)
setattr(plt1, "xrange", (fstart, fstop))
setattr(plt1.frame1, "draw_grid", true)
setattr(plt1.x1, "label", "Frequency, Hz")
setattr(plt1.y1, "label", "LPF out, dB")

a = Curve(freq, filt1, "color", "blue")
b = Curve(freq, filt2, "color", "black")
add(plt1, a)
add(plt1, b)