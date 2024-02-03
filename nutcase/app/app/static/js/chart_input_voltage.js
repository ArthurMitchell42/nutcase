//=================================================
// Draw the battery_charge chart
//=================================================
const chart_input_voltage_data = {
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
      label: 'Input Voltage',
  
      data: [ 0 ],
      fill: {
        target: 'origin',
        above: Chart_Input_Voltage_fill_above,
        // below: 'rgba(0, 0, 255, 0.2)'    // And blue below the origin
      },
      //Chart_Fill,
      tension:                    Chart_Tension,
      borderWidth:                Chart_Input_Voltage_borderWidth,
      borderColor:                Chart_Input_Voltage_borderColor,
      backgroundColor:            Chart_Input_Voltage_backgroundColor,
      pointBackgroundColor:       Chart_Input_Voltage_pointBackgroundColor,
      pointRadius:                Chart_Input_Voltage_pointRadius,
      pointBorderColor:           Chart_Input_Voltage_pointBorderColor,
      pointBorderWidth:           Chart_Input_Voltage_pointBorderWidth,
      pointHitRadius:             Chart_Input_Voltage_pointHitRadius,
      pointHoverBackgroundColor:  Chart_Input_Voltage_pointHoverBackgroundColor,
      }
    ]
  };
  
  const chart_input_voltage_plugins = {
    title: {
          text: 'Input Voltage',
          // display: false,
          display: true,
          align: Chart_Title_Align, 
          font: { size: Chart_Title_Size },
          color: Chart_Input_Voltage_Title_Colour
        },
    // subtitle: {
    //   // display: false,
    //       display: true,
    // position: Chart_Subtitle_Position,
    // align: Chart_Subtitle_Align,
    // color: Chart_Input_Voltage_Subtitle_Colour,
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
            // console.log(context)
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            if (context.parsed.y !== null) {
              // label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed.y);
              label += String(context.parsed.y) + 'V';
            }
            return label;
          }
        }
      }  
    };
  
  const chart_input_voltage_scales = {
    y: { 
      // position: 'right',
      title: {
          display: true,
          align: 'center',
          text: "Line Input /Volts",
          },
      max: null,
      min: null,
      },
    x: {
      autoSkip: false,
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
  
  const chart_input_voltage_options = {
      responsive: true,
      maintainAspectRatio: false,
      // onClick: myFunction,
      layout: {
        padding: 0,
      },
      plugins: chart_input_voltage_plugins,
      scales: chart_input_voltage_scales,

    };
  
  const chart_input_voltage_config = {
    type: 'line',
    data: chart_input_voltage_data,
    options: chart_input_voltage_options,
    // plugins: [plugin],
  };
  
  const chart_input_voltage_canvas = document.getElementById('chart_input_voltage').getContext('2d');
  var chart_input_voltage_obj = new Chart(chart_input_voltage_canvas, chart_input_voltage_config);
  
  