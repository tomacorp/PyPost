# Tom Anderson
# vdiv_filter.jl
# MIT License
# 10/30/2016
# Function library for an NGSpice post processor using the Julia repl

using Winston
import Winston.*

global const m = 1e-3
global const u = 1e-6
global const n = 1e-9
global const p = 1e-12
global const f = 1e-15
global const k = 1e3
global const K = 1e3
global const meg = 1e6
global const Meg = 1e6
global const M = 1e6
global const MEG = 1e6
global const G = 1e9
global const g = 1e9

vdiv(z1, z2) = (z2 + 0im) ./ (z1 + z2)
para(z1, z2) = (z1 + 0im) .* vdiv(z1, z2)

vdiv(z1::Array{Float64,1}, z2::Array{Float64,1}) = (z2 + 0im) ./ (z1 + z2)
para(z1::Array{Float64,1}, z2::Array{Float64,1}) = (z1 + 0im) .* vdiv(z1, z2)
vdiv(z1::Array{Complex,1}, z2::Array{Complex,1}) = z2 ./ (z1 + z2)
para(z1::Array{Complex,1}, z2::Array{Complex,1}) = z1 .* vdiv(z1, z2)
vdiv(z1::Array{Complex,1}, z2::Array{Float64,1}) = z2 ./ (z1 + z2)
para(z1::Array{Complex,1}, z2::Array{Float64,1}) = z1 .* vdiv(z1, z2)
vdiv(z1::Array{Float64,1}, z2::Array{Complex,1}) = z2 ./ (z1 + z2)
para(z1::Array{Float64,1}, z2::Array{Complex,1}) = z1 .* vdiv(z1, z2)

vdiv(z1::Float64, z2::Float64) = (z2 + 0im) / (z1 + z2)
para(z1::Float64, z2::Float64) = (z1 + 0im) * vdiv(z1, z2)
vdiv(z1::Complex, z2::Complex) = z2 / (z1 + z2)
para(z1::Complex, z2::Complex) = z1 * vdiv(z1, z2)
vdiv(z1::Complex, z2::Float64) = z2 / (z1 + z2)
para(z1::Complex, z2::Float64) = z1 * vdiv(z1, z2)
vdiv(z1::Float64, z2::Complex) = z2 / (z1 + z2)
para(z1::Float64, z2::Complex) = z1 * vdiv(z1, z2)

magn(x) =hypot(real(x), imag(x))

db(x) = 20.0 * log10(magn(x))
logsweep(x1, x2, npts) = logspace(log10(x1), log10(x2), npts)
zc(c,freq) = -(1im / (2π * c)) ./ freq
zl(l,freq) = 1im * 2π * l .* freq
zr(r,freq) = ones(Integer(length(freq))) * r
Base.max(x::Array{Float64,1})=maximum(x)
Base.min(x::Array{Float64,1})=minimum(x)


