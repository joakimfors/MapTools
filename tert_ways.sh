#!/bin/bash

# cat Scania_rough_border.osm |sed -n "s/.*lat='\([0-9\.]*\)'.*lon='\([0-9\.]*\)'.*/\1 \2/p" | tr "\n" " "

skane="56.57031873765874 12.812831098883597 56.37090906790887 13.16750951950267 56.44624803525686 13.462019279481007 56.55112309127424 14.092206830402397 56.47074482530082 14.522887769725555 56.23386669667398 14.605223831654984 55.47669746768843 14.716060838098445 55.14869917200607 13.38601676077692 55.35086529043879 12.64499220341207 55.62716752707318 12.879333302749671 55.89798459763238 12.613324487285364 56.03976537424884 12.64499220341207 56.51619696016169 12.138308745384819"

query="(\
	way(poly:'$skane')['highway'='tertiary']['ref'~'^M'];\
	rel(bw)['type'='route']['route'='road']['ref'~'^M'];\
);out meta;"

# Fixa så den söker på bara highway (secondary kan vara sekundär länsväg också… samma med residential/unclassified etc)

query="(\
	way(poly:'$skane')['highway']['ref'~'M'];\
	rel(bw)['type'='route']['route'='road']['ref'~'^M'];\
);out meta;"

curl -o "tert_ways.osm" --data "$query" "http://overpass-api.de/api/interpreter"

ret=$?

cat "tert_ways.osm"

exit $ret
