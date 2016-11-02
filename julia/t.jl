import Winston.*

m=1e-3
u=1e-6
n=1e-9
p=1e-12
f=1e-15
k=1e3
K=1e3
Meg=1e6
M=1e6
MEG=1e6
meg=1e6
G=1e-9

vdiv(z1, z2)= (z2 + 0im) ./ (z1 + z2)
para(z1, z2)= (z1 + 0im) .* vdiva(z1, z2)
magn(x)=hypot(real(x), imag(x))
db(x)= 20 * log10(magn(x))
logsweep(x1, x2, npts)=logspace(log10(x1), log10(x2), npts)
zc(c,freq)= -(1im / (2pi * c)) ./ freq
zl(l,freq)= 1im * 2pi * l .* freq
zr(r,freq)= ones(Integer(length(freq))) * r

fstart = 1
fstop = 10meg
npts = 2810
freq = logsweep(fstart, fstop, npts)

# filt = db(magn(vdiv(zr(1k,freq), zc(.01u,freq))))
filt = db(vdiv(zr(100,freq)+zl(1m,freq), zc(.01u,freq)))

p = FramedPlot()
setattr(p, "xlog", true)
setattr(p, "xrange", (fstart, fstop))
setattr(p.frame1, "draw_grid", true)
setattr(p.x1, "label", "Frequency, Hz")
setattr(p.y1, "label", "LPF out, dB")

a = Curve(freq, filt, "color", "blue")
add(p, a)
