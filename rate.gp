
set ylabel 'PPS offset(sec)'
set xlabel 'Elapsed Time(sec)'

f(x) = a*x + b

fit f(x) 'offset.txt' u 2:4  via a, b

rate=a*86400.0*365.0
offset=b

set title "Chr.Ward C7 Rapide Chronograph Mk2 v390 / Chronometer (ETA 251.264 COSC) (2016-Jan-06)"

plot 'ticks.txt' u 2:5 w p title 'raw offsets', f(x) title 'linear fit $rate spy', 'offset.txt' u 2:4 w p title 'inhibition (480s) average'