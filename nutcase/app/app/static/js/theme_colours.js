//=====================
// Theme colours
//=====================
const Theme_Green_Title_Colour              = getComputedStyle(document.documentElement).getPropertyValue('--bs-success')
const Theme_Green_Subtitle_Colour           = getComputedStyle(document.documentElement).getPropertyValue('--bs-success')
const Theme_Green_borderColor               = 'rgba(0, 160, 0, 0.3)'
const Theme_Green_backgroundColor           = 'rgba(0, 200, 0, 0.1)'
const Theme_Green_pointBorderColor          = 'rgba(0, 100, 0, 0.0)'
const Theme_Green_pointBackgroundColor      = 'rgba(0, 200, 0, 0.5)'
const Theme_Green_pointHoverBackgroundColor = 'rgba(200, 10, 10, 0.9)'
const Theme_Green_Chart_fill_above          = 'rgba(0, 200, 0, 0.1)'
const Theme_Green_Chart_pointRadius         = 3

const Theme_Gold_Title_Colour              = 'rgb(230, 155, 6)' //255,193,7 //getComputedStyle(document.documentElement).getPropertyValue('--bs-warning')
const Theme_Gold_Subtitle_Colour           = getComputedStyle(document.documentElement).getPropertyValue('--bs-warning')
const Theme_Gold_borderColor               = 'rgba(200, 200, 0, 0.3)'
const Theme_Gold_backgroundColor           = 'rgba(200, 200, 0, 0.1)'
const Theme_Gold_pointBorderColor          = 'rgba(100, 100, 0, 0.0)'
const Theme_Gold_pointBackgroundColor      = 'rgba(200, 200, 0, 0.5)'
const Theme_Gold_pointHoverBackgroundColor = 'rgba(200, 10, 10, 0.9)'
const Theme_Gold_Chart_fill_above          = 'rgba(200, 200, 0, 0.1)'
const Theme_Gold_Chart_pointRadius         = 3

const Theme_Blue_Title_Colour              = 'rgba( 13, 110, 253, 1.0)' //13,110,253   // 'rgb(' + getComputedStyle(document.documentElement).getPropertyValue('--bs-primary-rgb') + ')'
const Theme_Blue_Subtitle_Colour           = 'rgba( 13, 100, 230, 1.0)' // getComputedStyle(document.documentElement).getPropertyValue('--bs-primary')
const Theme_Blue_borderColor               = 'rgba(13, 110, 253, 0.3)'
const Theme_Blue_backgroundColor           = 'rgba(13, 110, 253, 0.1)'
const Theme_Blue_pointBorderColor          = 'rgba(0, 0, 200, 0.0)'
const Theme_Blue_pointBackgroundColor      = 'rgba(13, 110, 253, 0.5)'
const Theme_Blue_pointHoverBackgroundColor = 'rgba(200, 10, 10, 0.9)'
const Theme_Blue_Chart_fill_above          = 'rgba(13, 110, 253, 0.1)'
const Theme_Blue_Chart_pointRadius         = 3

const Theme_Red_Title_Colour              = 'rgba(180, 42, 56, 1.0)' // getComputedStyle(document.documentElement).getPropertyValue('--bs-danger')
const Theme_Red_Subtitle_Colour           = 'rgba(220, 53, 69, 1.0)' // getComputedStyle(document.documentElement).getPropertyValue('--bs-danger')
const Theme_Red_borderColor               = 'rgba(200,   0, 0, 0.3)'
const Theme_Red_backgroundColor           = 'rgba(200,   0, 0, 0.1)'
const Theme_Red_pointBorderColor          = 'rgba(200,   0, 0, 0.0)'
const Theme_Red_pointBackgroundColor      = 'rgba(200,   0, 0, 0.5)'
const Theme_Red_pointHoverBackgroundColor = 'rgba( 10, 200, 10, 0.9)'
const Theme_Red_Chart_fill_above          = 'rgba(200,   0, 0, 0.1)'
const Theme_Red_Chart_pointRadius         = 3

//=====================
// Chart configuration
//=====================
const Chart_Title_Size        = 18
const Chart_Subtitle_Size     = 16
const Chart_Title_Align       = 'start'   // start center end
const Chart_Subtitle_Align    = 'center'  // start center end
const Chart_Subtitle_Position = 'bottom'  // top left bottom right chartArea
const Chart_Fill              = true
const Chart_Tension           = 0.2
const Chart_borderWidth       = 3
const Chart_pointBorderWidth  = 5
const Chart_pointHitRadius    = 10
const Chart_spanGaps          = true
const Chart_Grid_Colour       = 'rgba( 100, 100, 100, 0.3)'

const Chart_Input_Voltage_borderColor               = Theme_Gold_borderColor
const Chart_Input_Voltage_backgroundColor           = Theme_Gold_backgroundColor
const Chart_Input_Voltage_borderWidth               = Chart_borderWidth
const Chart_Input_Voltage_pointBackgroundColor      = Theme_Gold_pointBackgroundColor
const Chart_Input_Voltage_pointBorderColor          = Theme_Gold_pointBorderColor
const Chart_Input_Voltage_pointBorderWidth          = Chart_pointBorderWidth
const Chart_Input_Voltage_pointHitRadius            = Chart_pointHitRadius
const Chart_Input_Voltage_pointHoverBackgroundColor = Theme_Gold_pointHoverBackgroundColor
const Chart_Input_Voltage_Subtitle_Colour           = Theme_Gold_Subtitle_Colour
const Chart_Input_Voltage_Title_Colour              = Theme_Gold_Title_Colour
const Chart_Input_Voltage_fill_above                = Theme_Gold_Chart_fill_above
const Chart_Input_Voltage_pointRadius               = Theme_Gold_Chart_pointRadius

const Chart_Battery_Charge_borderColor               = Theme_Blue_borderColor
const Chart_Battery_Charge_backgroundColor           = Theme_Blue_backgroundColor
const Chart_Battery_Charge_borderWidth               = Chart_borderWidth
const Chart_Battery_Charge_pointBackgroundColor      = Theme_Blue_pointBackgroundColor
const Chart_Battery_Charge_pointBorderColor          = Theme_Blue_pointBorderColor
const Chart_Battery_Charge_pointBorderWidth          = Chart_pointBorderWidth
const Chart_Battery_Charge_pointHitRadius            = Chart_pointHitRadius
const Chart_Battery_Charge_pointHoverBackgroundColor = Theme_Blue_pointHoverBackgroundColor
const Chart_Battery_Charge_Subtitle_Colour           = Theme_Blue_Subtitle_Colour
const Chart_Battery_Charge_Title_Colour              = Theme_Blue_Title_Colour
const Chart_Battery_Charge_fill_above                = Theme_Blue_Chart_fill_above
const Chart_Battery_Charge_pointRadius               = Theme_Blue_Chart_pointRadius

const Chart_Power_borderColor               = Theme_Green_borderColor
const Chart_Power_backgroundColor           = Theme_Green_backgroundColor
const Chart_Power_borderWidth               = Chart_borderWidth
const Chart_Power_pointBackgroundColor      = Theme_Green_pointBackgroundColor
const Chart_Power_pointBorderColor          = Theme_Green_pointBorderColor
const Chart_Power_pointBorderWidth          = Chart_pointBorderWidth
const Chart_Power_pointHitRadius            = Chart_pointHitRadius
const Chart_Power_pointHoverBackgroundColor = Theme_Green_pointHoverBackgroundColor
const Chart_Power_Subtitle_Colour           = Theme_Green_Subtitle_Colour
const Chart_Power_Title_Colour              = Theme_Green_Title_Colour
const Chart_Power_fill_above                = Theme_Green_Chart_fill_above
const Chart_Power_pointRadius               = Theme_Green_Chart_pointRadius

const Chart_Runtime_borderColor               = Theme_Red_borderColor
const Chart_Runtime_backgroundColor           = Theme_Red_backgroundColor
const Chart_Runtime_borderWidth               = Chart_borderWidth
const Chart_Runtime_pointBackgroundColor      = Theme_Red_pointBackgroundColor
const Chart_Runtime_pointBorderColor          = Theme_Red_pointBorderColor
const Chart_Runtime_pointBorderWidth          = Chart_pointBorderWidth
const Chart_Runtime_pointHitRadius            = Chart_pointHitRadius
const Chart_Runtime_pointHoverBackgroundColor = Theme_Red_pointHoverBackgroundColor
const Chart_Runtime_Subtitle_Colour           = Theme_Red_Subtitle_Colour
const Chart_Runtime_Title_Colour              = Theme_Red_Title_Colour
const Chart_Runtime_fill_above                = Theme_Red_Chart_fill_above
const Chart_Runtime_pointRadius               = Theme_Red_Chart_pointRadius

//=======================
// Dougnut configuration
//=======================
const Dougnut_Title_Size              = 18
const Dougnut_Subtitle_Size           = 16
const Dougnut_Center_Text_Size        = 24
const Dougnut_Center_Text_Size_Small  = 22
const Dougnut_Title_Align             = 'start'   // start center end
const Dougnut_Subtitle_Align          = 'center'   // start center end
const Dougnut_Subtitle_Position       = 'bottom'  // top left bottom right chartArea
const Dougnut_hoverOffset             = 4
const Dougnut_borderWidth             = 0
const Dougnut_circumference           = 270
const Dougnut_rotation                = 225
const Dougnut_Nominal_rgba            = 'rgba(128, 128, 128,   1)'
const Dougnut_Center_Text_colour      = 'rgba(128, 128, 128,   1)'
const Dougnut_Ring_Background_rgba    = 'rgba(128, 128, 128, 0.2)'

const Dougnut_Battery_Charge_Title_Colour       = Theme_Blue_Title_Colour
const Dougnut_Battery_Charge_Subtitle_Colour    = Theme_Blue_Subtitle_Colour
const Dougnut_Battery_Charge_Center_Text_Colour = Dougnut_Center_Text_colour

const Dougnut_Battery_Voltage_Title_Colour       = Theme_Green_Title_Colour
const Dougnut_Battery_Voltage_Subtitle_Colour    = Theme_Green_Subtitle_Colour
const Dougnut_Battery_Voltage_Center_Text_Colour = Dougnut_Center_Text_colour

const Dougnut_Input_Voltage_Title_Colour       = Theme_Gold_Title_Colour
const Dougnut_Input_Voltage_Subtitle_Colour    = Theme_Gold_Subtitle_Colour
const Dougnut_Input_Voltage_Center_Text_Colour = Dougnut_Center_Text_colour

const Dougnut_Power_Title_Colour        = Theme_Green_Title_Colour
const Dougnut_Power_Subtitle_Colour     = Theme_Green_Subtitle_Colour
const Dougnut_Power_Center_Text_Colour  = Dougnut_Center_Text_colour

// const plugin = {
//   id: 'customCanvasBackgroundColor',
//   beforeDraw: (chart, args, options) => {
//     const {ctx} = chart;
//     ctx.save();
//     ctx.globalCompositeOperation = 'destination-over';
//     ctx.fillStyle = options.color || '#99ff22';
//     ctx.fillRect(0, 0, chart.width, chart.height);
//     ctx.restore();
//   }
// };
