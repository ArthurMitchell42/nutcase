//=================================================
// Draw the power chart
//=================================================
const chart_power_data = {
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
        above: Chart_Power_fill_above,
        // below: 'rgba(0, 0, 255, 0.2)'    // And blue below the origin
      },
      //Chart_Fill,
      tension:                    Chart_Tension,
      borderWidth:                Chart_Power_borderWidth,
      borderColor:                Chart_Power_borderColor,
      backgroundColor:            Chart_Power_backgroundColor,
      pointBackgroundColor:       Chart_Power_pointBackgroundColor,
      pointRadius:                Chart_Power_pointRadius,
      pointBorderColor:           Chart_Power_pointBorderColor,
      pointBorderWidth:           Chart_Power_pointBorderWidth,
      pointHitRadius:             Chart_Power_pointHitRadius,
      pointHoverBackgroundColor:  Chart_Power_pointHoverBackgroundColor,
    }
    ]
  };
  
  const chart_power_plugins = {
    title: {
          text: 'Output Power',
          // display: false,
          display: true,
          align: Chart_Title_Align,
          font: { size: Chart_Title_Size },
          color: Chart_Power_Title_Colour

        },
    // subtitle: {
    //   // display: false,
    //       display: true,
    // position: Chart_Subtitle_Position,
    //   color: Chart_Power_Subtitle_Colour
    // align: Chart_Subtitle_Align,
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
    },  
  };
  
  const chart_power_scales = {
    y: { 
      position: 'right',
      title: {
          display: true,
          align: 'center',
          text: "% Capacity",
          },
      max: 100,
      min:   0,
      },
    y1: { 
      position: 'left',
      title: {
          display: true,
          align: 'center',
          text: "Watts",
          },
      grid: {
          drawOnChartArea: false, // only want the grid lines for one axis to show up
        },
      max: 500,
      min:   0,
      },
      // xAxes: {
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
    };
  
  const chart_power_options = {
      responsive: true,
      maintainAspectRatio: false,
      // onClick: myFunction,
      layout: {
        padding: 0,
      },
      plugins: chart_power_plugins,
      scales: chart_power_scales
    };
  
  const chart_power_config = {
    type: 'line',
    data: chart_power_data,
    options: chart_power_options,
  };
  
  const chart_power_canvas = document.getElementById('chart_power').getContext('2d');
  var chart_power_obj = new Chart(chart_power_canvas, chart_power_config);
  