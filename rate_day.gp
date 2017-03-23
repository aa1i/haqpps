#date="2016-Apr-05"
date=system("date +%Y-%b-%d")

# watch info

# 01 Ti
#watch='Longines VHP Ti "01" Cal 174.2 ETA 255.561'
# 02
#watch='Longines VHP "02" Cal 174.2 ETA 255.561'
# 03 PC
#watch='Longines VHP PC Cal L1.627.3'
# 05
#watch='Longines VHP "05" Cal L174 ETA 255.561(malfunctioning)'
# 06 PC S/N 28727869
watch='Longines VHP PC "06" Cal L1.627.4 S/N 28727869'
# 08 L174.2 S/N 22091820
#watch='Longines VHP "08" Cal L174.2 ETA 255.561 S/N 22091820'
#watch='Longines VHP "09" Cal L208.2'
# 10 pc
#watch='Longines VHP PC "10" Cal L1.636.4 ETA ? S/N ?'
# 11 lost in mail
# 12 ti un-recorded
#watch='Longines VHP ti "12" Cal TBD '
# 13 PC "blue"
#watch='Longines VHP PC "13" Cal L1.636.4 ETA ?252.531? S/N 29206563'
# 14 ti
#watch='Longines VHP Ti "14" Cal 174.? S/N 22222759'
# 15 PC
#watch='Longines VHP PC "15" Cal L1.636.4 ETA ?252.531? S/N 29206269'
limit=2.0  # VHP

#watch='Chr.Ward C7 Rapide Chronograph Mk2 v390 / Chronometer (ETA 251.264 COSC)'
#limit=10.0 # COSC

#watch='Certina DS-2 3-hand Precidrive ETA F06.411'
#limit=10.0 # PreciDrive

#inhib=10
#inhib=60
inhib=480
#inhib=960

int_seconds=0.0

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


# fit parameters

f(x) = a*x + b

fit f(x) 'offset.txt' u ($2/span):(int_seconds - $4)  via a, b


#bound=limit/(span*365.0) 
bound=limit/((86400.0/span)*365.0) 

rate=a*(86400.0/span)*365.0
offset=b

print rate

g(x)=bound*x+b
h(x)=-bound*x+b 


# plot

plot 'ticks.txt' u ($2/span):(int_seconds - $5) w p title 'raw offsets',\
     f(x) title sprintf("linear fit %.1f spy", rate),\
     'offset.txt' u ($2/span):(int_seconds - $4) w p title sprintf("inhibition (%ds) average", inhib),\
     g(x) w l lc 'black' title sprintf("%d spy",  limit),\
     h(x) w l lc 'black' title sprintf("%d spy", -limit)



pause -1 "press <ret> to exit"
