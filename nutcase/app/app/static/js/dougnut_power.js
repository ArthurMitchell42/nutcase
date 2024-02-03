//=================================================
// Draw the power doughnut
//=================================================
const dougnut_power_data = {
    labels: [
      'Power',
      '',
      'Normal',
      'Overload',
    ],
    datasets: [
    {
    label: 'Output Power',
    data: [ 0, 1 ], 
    tooltip: {
      callbacks: {
        label: function(tooltipItem) {
          // console.log(tooltipItem)
          let label = ""
          // if (tooltipItem.dataIndex === 0) {
          //   label = tooltipItem.label || ''; 
          // } else {
            label = tooltipItem.dataset.label || ''; 
          // }
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
        'rgba( 46, 119,  46, 1)',
        // 'rgba(  0,   0,   0, 0)',
        Dougnut_Ring_Background_rgba,
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
      data: [ 1, 0, 0, 0 ],
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
        'rgba( 46, 119,  46, 1)',
        'rgba(199,   0,  57, 1)',
      ],
      hoverOffset: Dougnut_hoverOffset,
      borderWidth: Dougnut_borderWidth,
      circumference: Dougnut_circumference,
      rotation: Dougnut_rotation,
      cutout: '90%',
      radius: '90%',
      animation: {animateRotate: false,}
    }
  ]
  };
  
  const dougnut_power_plugins = {
    title: {
          text: 'Output',
          display: true,
          align: Dougnut_Title_Align, 
          font: { size: Dougnut_Title_Size },
          color: Dougnut_Power_Title_Colour
        },
    subtitle: {
          display: true,
          position: Dougnut_Subtitle_Position,
          align: Dougnut_Subtitle_Align,
          color: Dougnut_Power_Subtitle_Colour,
          text: 'Power',
          font: { size: Dougnut_Subtitle_Size },
          },
    legend: {
      display: false,
      position: 'right', // top left bottom right chartArea
      },
    tooltip: {
      callbacks: {
        title: function(tooltipItems) {
          // console.log(tooltipItems);
          if (tooltipItems[0].datasetIndex === 0) {
            return tooltipItems[0].dataset.label
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
          color: Dougnut_Power_Center_Text_Colour,
          content: ['--W', "--%"],
          font: {
            size: Dougnut_Center_Text_Size_Small
          }
        }
      }
    }
  };
  
  const dougnut_power_options = {
      responsive: true,
      layout: {
        padding: 0,
      },
      plugins: dougnut_power_plugins,
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
  
  const dougnut_power_config = {
    type: 'doughnut',
    data: dougnut_power_data,
    // plugins: cpu_plugins,
    options: dougnut_power_options,
  };
  
  const power_canvas = document.getElementById('dougnut_power').getContext('2d');
  var power_dougnut_obj = new Chart(power_canvas, dougnut_power_config);
