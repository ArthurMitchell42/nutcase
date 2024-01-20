//=================================================
// Draw the battery_charge chart
//=================================================
const chart_battery_charge_data = {
    labels: [
      '-15m',
      '',
      '-10m',
      '',
      '-5m',
      '',
      'Now'
      ],
    datasets: [
      {
      label: 'Output Power',
      data: [ 0 ],
      fill: {
        target: 'origin',
        above: Chart_Battery_Charge_fill_above,
        // below: 'rgba(0, 0, 255, 0.2)'    // And blue below the origin
      },
      //Chart_Fill,
      tension:                    Chart_Tension,
      borderWidth:                Chart_Battery_Charge_borderWidth,
      borderColor:                Chart_Battery_Charge_borderColor,
      backgroundColor:            Chart_Battery_Charge_backgroundColor,
      pointBackgroundColor:       Chart_Battery_Charge_pointBackgroundColor,
      pointRadius:                Chart_Input_Voltage_pointRadius,
      pointBorderColor:           Chart_Battery_Charge_pointBorderColor,
      pointBorderWidth:           Chart_Battery_Charge_pointBorderWidth,
      pointHitRadius:             Chart_Battery_Charge_pointHitRadius,
      pointHoverBackgroundColor:  Chart_Battery_Charge_pointHoverBackgroundColor,
      }
      ]
    };

  const chart_battery_charge_plugins = {
    title: {
        text: 'Battery Charge',
        // display: false,
        display: true,
        align: Chart_Title_Align, 
        font: { size: Chart_Title_Size },
        color: Chart_Battery_Charge_Title_Colour
    },
    // subtitle: {
    //   // display: false,
    //       display: true,
    // position: Chart_Subtitle_Position,
    // align: Chart_Subtitle_Align,
    // color: Chart_Battery_Charge_Subtitle_Colour,
//       text: 'Charge',
    //       font: { size: Chart_Subtitle_Size },
    //       },
    legend: {
        display: false,
        position: 'right', // top left bottom right chartArea
      },

    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
              label += ': ';
          }
          if (context.parsed.y !== null) {
            // label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
            label += String(context.parsed.y) + '%';
          }
          return label;
        }
      }
    }
  };
  
  const chart_battery_charge_scales = {
    y: { 
      // position: 'right',
      title: {
          display: true,
          align: 'center',
          text: "% Charge",
          },
      max: 100,
      },
    x: {
      ticks: {
          autoSkip: false,
          // maxRotation: 90,
          // minRotation: 90
      },
      grid: {
        autoSkip: false,
        color: [ null, null, null, null, null, null, null, null, null, Chart_Grid_Colour ],
      },
    }
  }

  const chart_battery_charge_options = {
      responsive: true,
      maintainAspectRatio: false,
      // onClick: myFunction,
      layout: {
        padding: 0,
      },
      plugins: chart_battery_charge_plugins,
      scales: chart_battery_charge_scales,
    };
  
  const chart_battery_charge_config = {
    type: 'line',
    data: chart_battery_charge_data,
    options: chart_battery_charge_options,
    // plugins: [plugin],
  };
  
  const chart_battery_charge_canvas = document.getElementById('chart_battery_charge').getContext('2d');
  var chart_battery_charge_obj = new Chart(chart_battery_charge_canvas, chart_battery_charge_config);
  