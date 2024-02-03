//=================================================
// Draw the battery_charge doughnut
//=================================================
const dougnut_battery_charge_data = {
    labels: [
      'Battery Charge',
      '',
      'Shutdown',
      'Warning',
      'OK',
    ],
    datasets: [
    {
    label: 'Current Charge',
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
            label += String(tooltipItem.parsed) + '%';
          } else {
            label += String(tooltipItem.dataset.data[0]) + '%';
          }
          return label;
        }
      }
    },
    backgroundColor: [
        'rgba( 46, 119, 46,   1)',
        Dougnut_Ring_Background_rgba,
        // 'rgba(200, 200, 200,  0)',
      ],
      hoverOffset: Dougnut_hoverOffset,
      borderWidth: Dougnut_borderWidth,
      circumference: Dougnut_circumference,
      rotation: Dougnut_rotation,
      cutout: '80%',
      radius: '100%',
  },
    {
      label: 'Range',
      data: [ 1, 0, 0, 0, 0 ],
      tooltip: {
        callbacks: {
          label: function(tooltipItem) {
            let from_value = 0;
            let to_value = tooltipItem.dataset.data[0];
  
            for (let index = 0; index < tooltipItem.dataIndex; index++) {
              from_value += tooltipItem.dataset.data[index]
              to_value += tooltipItem.dataset.data[index+1]
            }
  
            let label = tooltipItem.dataset.label || '';
            if (label) {
                label += ': ';
            }
            label += String(from_value) + '-' + String(to_value) + '%';
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
      cutout: '90%',
      radius: '85%',
      animation: {animateRotate: false,}
    }
  ]
  };
  
  const dougnut_battery_charge_plugins = {
    title: {
          text: 'Battery',
          // display: false,
          display: true,
          align: Dougnut_Title_Align, 
          font: { size: Dougnut_Title_Size },
          color: Dougnut_Battery_Charge_Title_Colour
        },
    subtitle: {
      // display: false,
          display: true,
          position: Dougnut_Subtitle_Position,
          align: Dougnut_Subtitle_Align,
          color: Dougnut_Battery_Charge_Subtitle_Colour,
          text: 'Charge',
          font: { size: Dougnut_Subtitle_Size },
          },
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
            label += String(context.parsed) + '%';
          }
          return label;
        }
      }
    },
    annotation: {
      // clip: false,
      clip: true,
      annotations: {
        label1: {
          type: 'label',
          position: 'center',
          textAlign: 'center',

          xAdjust: 0,
          yAdjust: 10,
          // xValue: 0,
          // xAdjust: 0,
          // yValue: 0,
          // yAdjust: 50,
          // height: "50%",
          color: Dougnut_Battery_Charge_Center_Text_Colour,
          content: [ '--%' ],
          font: {
            size: Dougnut_Center_Text_Size
          }
        }
      }
    }
  };

  const dougnut_battery_charge_options = {
      responsive: true,
      // onClick: myFunction,
      layout: {
        padding: 0,
      },
      plugins: dougnut_battery_charge_plugins,
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
  
  const dougnut_battery_charge_config = {
    type: 'doughnut',
    data: dougnut_battery_charge_data,
    options: dougnut_battery_charge_options,
  };
  
  const dougnut_battery_charge_canvas = document.getElementById('dougnut_battery_charge').getContext('2d');
  var dougnut_battery_charge_obj = new Chart(dougnut_battery_charge_canvas, dougnut_battery_charge_config);
  