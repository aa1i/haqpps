
set ylabel 'PPS offset(sec)'
set xlabel 'Elapsed Time(sec)'

f(x) = a*x + b
watch='Chr.Ward C7 Rapide Chronograph Mk2 v390 / Chronometer (ETA 251.264 COSC)'
watch='Longines VHP Ti Cal 174.2 ETA 255.561'
date="2016-Jan-06"

fit f(x) 'offset.txt' u 2:4  via a, b

rate=a*86400.0*365.0
offset=b

#set title "Chr.Ward C7 Rapide Chronograph Mk2 v390 / Chronometer (ETA 251.264 COSC) (2016-Jan-06)"
set title watch." (".date.")"

#plot 'ticks.txt' u 2:5 w p title 'raw offsets', f(x) title 'linear fit $rate spy', 'offset.txt' u 2:4 w p title 'inhibition (480s) average'
plot 'ticks.txt' u 2:5 w p title 'raw offsets', f(x) title sprintf("linear fit %.1f spy", rate), 'offset.txt' u 2:4 w p title 'inhibition (480s) average'
set xlabel 'Elapsed Time(hrs)'
fit f(x) 'offset.txt' u ($2/3600):4  via a, b
rate=a*24.0*365.0
offset=b ; print rate
plot 'ticks.txt' u ($2/3600):5 w p title 'raw offsets',f(x) title sprintf("linear fit %.1f spy", rate),   'offset.txt' u ($2/3600):4 w p title 'inhibition (480s) average'
plot 'ticks.txt' u ($2/3600):5 w p title 'raw offsets',f(x) title sprintf("linear fit %.1f spy", rate),   'offset.txt' u ($2/3600):4 w p title 'inhibition (480s) average'
gnuplot> g(x)=bound*x+b
gnuplot> h(x)=-bound*x+b
plot 'ticks.txt' u ($2/3600):5 w p title 'raw offsets',f(x) title sprintf("linear fit %.1f spy", rate),   'offset.txt' u ($2/3600):4 w p title 'inhibition (480s) average',g(x) title '+2 spy',h(x) title '-2 spy'
plot 'ticks.txt' u ($2/3600):5 w p title 'raw offsets',f(x) title sprintf("linear fit %.1f spy", rate),   'offset.txt' u ($2/3600):4 w p title 'inhibition (480s) average',g(x) w l lc 'black' title '+2 spy',h(x) w l lc 'black' title '-2 spy'
set xlabel 'Elapsed Time(days)'
bound=2.0/365.0
gnuplot> g(x)=bound*x+b
gnuplot> h(x)=-bound*x+b
gnuplot> plot 'ticks.txt' u ($2/86400):5 w p title 'raw offsets',f(x) title sprintf("linear fit %.1f spy", rate),   'offset.txt' u ($2/86400):4 w p title 'inhibition (480s) average',g(x) w l lc 'black' title '+2 spy',h(x) w l lc 'black' title '-2 spy'
watch='Longines VHP PC Cal L1.627.3'
watch='Longines VHP Cal 174.2 ETA 255.561'
bound=2.0/(86400.0*365.0)
set xlabel 'Elapsed Time(sec)'
fit f(x) 'offset.txt' u 2:4  via a, b
rate = a*86400.0*365.0;  print rate ; g(x)=bound*x+b ; h(x)=-bound*x+b 
plot 'ticks.txt' u 2:5 w p title 'raw offsets',f(x) title sprintf("linear fit %.1f spy", rate),   'offset.txt' u 2:4 w p title 'inhibition (480s) average',g(x) w l lc 'black' title '+2 spy',h(x) w l lc 'black' title '-2 spy'
set format y "%.3f"
plot 'ticks.txt' u ($2/86400.0):5 w p title 'raw offsets',f(x) title sprintf("linear fit %.1f spy", rate),   'offset.txt' u ($2/86400.0):4 w p title 'inhibition (480s) average',g(x) w l lc 'black' title '+2 spy',h(x) w l lc 'black' title '-2 spy'
rate = a*365.0;  print rate ; g(x)=bound*x+b ; h(x)=-bound*x+b
bound=2.0/(365.0)
fit f(x) 'offset.txt' u ($2/86400.0):4  via a, b
