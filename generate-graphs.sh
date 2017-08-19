#!/bin/bash

for i in `seq 1 $1`;
do
  geng -c $i input$i
  showg -Aq input$i graphs$i
done
