//=================================================
// Draw the battery_voltage doughnut
//=================================================
const dougnut_battery_voltage_data = {
    labels: [
      'Voltage',
      '',
      'Shutdown',
      'Warning',
      'OK',
      ''
    ],
    datasets: [
    {
    label: 'Voltage',
    data: [ 0, 1 ], 
    tooltip: {
      callbacks: {
        label: function(tooltipItem) {
          let label = ""
            label = tooltipItem.dataset.label || ''; 
          if (label) {
              label += ': ';
          }
          if (tooltipItem.dataIndex === 0) {
            label += String(tooltipItem.parsed) + 'V';
          } else {
            label += String(tooltipItem.dataset.data[0]) + 'V';
          }
          return label;
        }
      }
    },
    backgroundColor: [
        'rgba( 46, 119,  46, 1)',
        Dougnut_Ring_Background_rgba,
        // 'rgba(  0,   0,   0, 0)',
      ],
      hoverOffset: Dougnut_hoverOffset,
      borderWidth: Dougnut_borderWidth,
      circumference: Dougnut_circumference,
      rotation: Dougnut_rotation,
      cutout: '70%',
      radius: '100%',
  },
    {
      label: 'Range',
      data: [ 1, 0, 0, 0, 0 ],
      tooltip: {
        callbacks: {
          // label: function(context, tooltipItems) {
          label: function(tooltipItem) {
            // console.log(tooltipItem)
            let from_value = 0;
            let to_value = tooltipItem.dataset.data[0];
  
            for (let index = 0; index < tooltipItem.dataIndex; index++) {
              from_value += tooltipItem.dataset.data[index]
              to_value += tooltipItem.dataset.data[index+1]
            }
  
            // console.log("from_value: " + from_value + " to_value: " + to_value)
            let label = tooltipItem.dataset.label || '';
            if (label) {
                label += ': ';
            }
            label += String(from_value) + '-' + String(to_value) + 'V';
            return label;
          }
        }
      },
      backgroundColor: [
        Dougnut_Ring_Background_rgba,
        // 'rgba(  0,   0,   0, 0)',
        'rgba(  0,   0,   0, 0)',
        'rgba(199,   0,  57, 1)',
        'rgba(255, 239,   0, 1)',
        'rgba( 46, 119,  46, 1)',
      ],
      hoverOffset: Dougnut_hoverOffset,
      borderWidth: Dougnut_borderWidth,
      circumference: Dougnut_circumference,
      rotation: Dougnut_rotation,
      cutout: '85%',
      radius: '80%',
      animation: {animateRotate: false,}
    },
    {
      label: 'Nominal',
      data: [ 0, 0, 0 ],
      tooltip: {
        callbacks: {
          label: function(tooltipItem) {
            let label = tooltipItem.dataset.label || '';
            if (label) {
                label += ': ';
            }
            let nom = tooltipItem.dataset.data[0] +(tooltipItem.dataset.data[1]/2);
            label += nom + 'V';
            return label;
          }
        }
      },
      backgroundColor: [
      'rgba(  0,   0,   0,   0)', 
      Dougnut_Nominal_rgba,
      'rgba(  0,   0,   0,   0)', 
      ],
      hoverOffset: Dougnut_hoverOffset,
      borderWidth: Dougnut_borderWidth,
      circumference: Dougnut_circumference,
      rotation: Dougnut_rotation,
      cutout: '80%',
      radius: '100%',
      animation: {animateRotate: false,}
    }
  ]
  };
  
  const dougnut_battery_voltage_plugins = {
    title: {
          text: 'Battery',
          display: true,
          align: Dougnut_Title_Align, 
          font: { size: Dougnut_Title_Size },
          color: Dougnut_Battery_Voltage_Title_Colour
        },
    subtitle: {
          display: true,
          position: Dougnut_Subtitle_Position,
          align: Dougnut_Subtitle_Align,
          text: 'Volts',
          font: { size: Dougnut_Subtitle_Size },
          color: Dougnut_Battery_Voltage_Subtitle_Colour
          },
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
            label += String(context.parsed) + 'V';
          }
          return label;
        }
      }
    },
    tooltip: {
      callbacks: {
        title: function(tooltipItems) {
          // console.log(tooltipItems);
          if (tooltipItems[0].datasetIndex === 0) {
            return tooltipItems[0].dataset.label
          } else {
            if (tooltipItems[0].datasetIndex === 2) {
              return tooltipItems[0].dataset.label
            } 
          }
          return
        },
      }
    },
    annotation: {
      clip: false,
      annotations: {
        label1: {
          type: 'label',
          position: 'center',
          xAdjust: 0,
          yAdjust: 10,
          // xValue: 0,
          // xValue: 0,
          // xAdjust: 0,
          // yValue: 0,
          // yAdjust: 50,
          color: Dougnut_Battery_Voltage_Center_Text_Colour,
          content: [ '--V' ],
          font: {
            size: Dougnut_Center_Text_Size
            }
          }
        }
      }
    };
  
  const dougnut_battery_voltage_options = {
    responsive: true,
    layout: {
    padding: 0,
    },
    plugins: dougnut_battery_voltage_plugins,
    scales: {
      x: {
        type: 'linear',
        position: 'right',
        display: false
      },
      y: {
        type: 'linear',
        position: 'bottom',
        display: false
      }
    }
};
  
  const dougnut_battery_voltage_config = {
    type: 'doughnut',
    data: dougnut_battery_voltage_data,
    options: dougnut_battery_voltage_options,
  };
  
  const dougnut_battery_voltage_canvas = document.getElementById('dougnut_battery_voltage').getContext('2d');
  var dougnut_battery_voltage_obj = new Chart(dougnut_battery_voltage_canvas, dougnut_battery_voltage_config);
