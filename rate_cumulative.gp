#date="2016-Apr-05"
date=system("date +%Y-%b-%d")

# watch info

# 01 Ti
#watch='Longines VHP Ti Cal 174.2 ETA 255.561'
# 02
#watch='Longines VHP "02" Cal 174.2 ETA 255.561'
# 03 PC
#watch='Longines VHP PC Cal L1.627.3'
# 06 PC S/N 28727869
watch='Longines VHP PC "06" Cal L1.627.4'
limit=2.0  # VHP

#watch='Chr.Ward C7 Rapide Chronograph Mk2 v390 / Chronometer (ETA 251.264 COSC)'
#limit=10.0 # COSC

#watch='Certina DS-2 3-hand Precidrive ETA F06.411'
#limit=10.0 # PreciDrive

#inhib=10
#inhib=60
inhib=480
#inhib=960



# time span of measurement

span=86400.0 # day
set xlabel 'Elapsed Time(days)'

#span=3600.0  # hr
#set xlabel 'Elapsed Time(hrs)'

#span=1.0     # sec
#set xlabel 'Elapsed Time(sec)'



# plot labels
set title watch." (".date.")"

set ylabel 'PPS offset(sec)'
set format y "%.3f"

time0=system("head -n 1 offset_cumulative.txt | cut -d' ' -f1")
print "time0: ".time0

# fit parameters

f(x) = a*x + b

fit f(x) 'offset_cumulative.txt' u (($1-time0)/span):4  via a, b


#bound=limit/(span*365.0) 
bound=limit/((86400.0/span)*365.0) 

rate=a*(86400.0/span)*365.0
offset=b

print "rate:"
print rate

g(x)=bound*x+b
h(x)=-bound*x+b 


# plot

plot f(x) lc 'green' title sprintf("linear fit %.1f spy", rate),\
     'offset_cumulative.txt' u (($1-time0)/span):4 w p lc 'blue' title sprintf("inhibition (%ds) average", inhib),\
     g(x) w l lc 'black' title sprintf("%d spy",  limit),\
     h(x) w l lc 'black' title sprintf("%d spy", -limit)



pause -1 "press <ret> to exit"
