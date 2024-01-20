//=================================================
// Draw the battery_charge chart
//=================================================
const runtime_data = {
    labels: [
      '',
      '-20m',
      '',
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
      label: 'Runtime',
      data: [ 0 ],
      fill: {
        target: 'origin',
        above: Chart_Runtime_fill_above,
        // below: 'rgba(0, 0, 255, 0.2)'    // And blue below the origin
      },
      //Chart_Fill,
      spanGaps:                   Chart_spanGaps,
      tension:                    Chart_Tension,
      borderWidth:                Chart_Runtime_borderWidth,
      borderColor:                Chart_Runtime_borderColor,
      backgroundColor:            Chart_Runtime_backgroundColor,
      pointRadius:                Chart_Runtime_pointRadius,
      pointBackgroundColor:       Chart_Runtime_pointBackgroundColor,
      pointBorderColor:           Chart_Runtime_pointBorderColor,
      pointBorderWidth:           Chart_Runtime_pointBorderWidth,
      pointHitRadius:             Chart_Runtime_pointHitRadius,
      pointHoverBackgroundColor:  Chart_Runtime_pointHoverBackgroundColor,
      }
    ]
  };
  
  const runtime_plugins = {
    title: {
        text: 'Battery Runtime',
        // display: false,
        display: true,
        align: Chart_Title_Align, 
        font: { size: Chart_Title_Size },
        color: Chart_Runtime_Title_Colour
    },
    // subtitle: {
    //   // display: false,
    //       display: true,
    // position: Chart_Subtitle_Position,
    // align: Chart_Subtitle_Align,
    // color: Chart_Runtime_Subtitle_Colour,
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
            label += String(context.parsed.y) + ' min';
          }
          return label;
        }
      }
    }
  };
  
  const runtime_scales = {
    y: { 
      // position: 'right',
      title: {
          display: true,
          align: 'center',
          // text: "Time /s",
          text: "Time /min",
          },
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
  
  const runtime_options = {
      responsive: true,
      maintainAspectRatio: false,
      // onClick: myFunction,
      layout: {
        padding: 0,
      },
      plugins: runtime_plugins,
      scales: runtime_scales,
    };
  
  const runtime_config = {
    type: 'line',
    data: runtime_data,
    options: runtime_options,
    // plugins: [plugin],
  };
  
  const runtime_canvas = document.getElementById('chart_runtime').getContext('2d');
  var runtime_chart_obj = new Chart(runtime_canvas, runtime_config);
  