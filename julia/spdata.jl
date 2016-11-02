#
# NGSpice raw data file parser
# Tom Anderson
# MIT License
# 10/30/2016
#

using Winston
import Winston.*

include("/Users/toma/tools/julia/rc_graph.jl")

function read_raw_file(filename::String)

    in_header = 1
    in_variables = 2
    in_data = 3

    no_points = 0
    no_variables = 0
    sweep_type = 1

    section = in_header

    fd = open(filename)

    while (section === in_header)
        line = readline(fd)
        if section === in_header
            header_match = match(r"^([^:]+):\s+(.*)", line)
            if header_match !== nothing
                directive = header_match.captures[1]
                value = header_match.captures[2]
                print(directive, " = ", value,"\n")
                if directive == "No. Variables"
                    no_variables = parse(Int64, value)
                elseif directive == "No. Points"
                    no_points = parse(Int64, value)
                elseif directive == "Variables"
                    section = in_variables
                elseif directive == "Flags"
                    if value == "complex"
                        sweep_type = 2
                    end
                end
            end
        end
    end

    while (section === in_variables)
        line = readline(fd)
        variable_match = match(r"\s+(\S+)\s+(\S+)\s+(\S*)", line)
        if variable_match !== nothing
            var_idx = variable_match[1]
            var_name = variable_match[2]
            var_type = variable_match[3]
            print("variable ", var_name, " has type ", var_type, "\n")
        else
            section = in_data
        end
    end

    print("Number of points ", no_points, "\n")
    print("Number of variables ", no_variables, "\n")
    out = Array{Float64}(no_variables, no_points)
    for step = 1:no_points
        for n = 1:no_variables
            if sweep_type == 1
                datum = read(fd, Float64)
            elseif sweep_type == 2
                datum_real = read(fd, Float64)
                datum_imag = read(fd, Float64)
                datum = hypot(datum_real, datum_imag)
            end
            out[n, step] = datum
            # print(datum, ", ")
        end
        # print("\n")
    end
    close(fd)
    return out
end

function plt(waveform)
    fstart=minimum(d[1,:])
    fstop=maximum(d[1,:])

    p = FramedPlot()
    setattr(p, "xlog", true)
    setattr(p, "xrange", (fstart, fstop))
    setattr(p.frame1, "draw_grid", true)
    setattr(p.x1, "label", "Frequency, Hz")
    setattr(p.y1, "label", "LPF out, dB")

    freq=d[1,:]
    v2=Curve(freq, waveform, "color", "red")
    add(p, v2)
end

function vdb(n)
    return db(d[n, :])
end

global map = 1
global d = read_raw_file("/Users/toma/tools/julia/t.raw")

# Need to have two environments: 
#   One for complex, and one for real.
#   Mixing them will just make a mess, at least at first.
#
# Make example file.
# Subcircuits need push and pop
# The name -> integer row mapper has a context variable.
# The outermost is the global, and it has subcircuits with dot-separated net names
# and component names.
#
# WIBNI Components get values from the netlist or simulator output.
# 
#
# 1. Set globals for all the variables in d that are not integer node names.
# The variables are just used to map their row numbers.  eg vin=1, vout=2.

# There is a final map of integer -> matrix row.
# (String|int) -> int -> row number.
# The integer node names get mapped to their rows in a fixed structure.

# 2. Function v(node): If the arg is an array, return the arg.
# If the arg is an integer, return the array that is mapped by the integer.

# 3. All the node names are just integers that map to where the integer indexes are stored,
# and all the row numbers are integers that map to where the integer indexes are.
# This is needed because integer net names might have large values. Since these are
# globals, they would hurt performance so use the const declaration to solve the
# problem.
#   global const vout=3



plt(vdb(3))
