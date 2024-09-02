//==============================================================================
//
// Title:		TLUP
// Purpose:		Thorlabs UP Series VISA instrument driver header file
//
// Created on:	04.02.2019 at 10:50:01 by Diethelm Krause.
// Copyright:	Thorlabs GmbH. All Rights Reserved.
//
//==============================================================================

#ifndef _TLUP_DRIVER_HEADER_
#define _TLUP_DRIVER_HEADER_

#include <vpptype.h> 

#if defined(__cplusplus) || defined(__cplusplus__)
extern "C" 
{
#endif

//==============================================================================
// Macros
#if defined _WIN32
    #if defined(_MSC_VER)
        #if defined(TLUP_EXPORT)
            #define TLUP_API __declspec(dllexport)
        #else
            #define TLUP_API __declspec(dllimport)
        #endif
    #else
        #if defined(TLUP_EXPORT)
            #define TLUP_API __attribute__ ((dllexport))
        #else
            #define TLUP_API __attribute__ ((dllimport))
        #endif
    #endif
    #define TLUP_INTERNAL /**/
#else
    #if __GNUC__ >= 4
        #define TLUP_API __attribute__ ((visibility ("default")))
        #define TLUP_INTERNAL  __attribute__ ((visibility ("hidden")))
    #else
        #define TLUP_API
        #define TLUP_INTERNAL
    #endif
#endif

		
/*
A name in all uppercase is a macro name. Example: VI_ATTR_TERMCHAR
*/

/*========================================================================*//**
\defgroup   TLUP_VID_PID_x  USB instrument identification
\ingroup    TLUP_MACROS_x
@{
*//*=========================================================================*/
#define TL_VID_THORLABS              (0x1313)   // Thorlabs Company
#define TLUP_PID_TEC_DFU             (0x8101)   // upTEC  with DFU interface enabled
#define TLUP_PID_TEMP_DFU            (0x8102)   // upTEMP with DFU interface enabled
#define TLUP_PID_LED_DFU             (0x8103)   // upLED  with DFU interface enabled
#define TLUP_PID_POWER_DFU           (0x8104)   // upPOWER  with DFU interface enabled
/**@}*/  /* TLUP_VID_PID_x */

/*========================================================================*//**
\defgroup   TLUP_BUFFERS_x  Buffers
\ingroup    TLUP_MACROS_x
@{
*//*=========================================================================*/
#define TLUP_BUFFER_SIZE            256     ///< General buffer size
#define TLUP_ERR_DESCR_BUFFER_SIZE  512     ///< Buffer size of error messages
#define TLUP_DATASET_NAME_SIZE       80     ///< Buffer size of data set name
/**@}*/  /* TLUP_BUFFERS_x */

/*========================================================================*//**
\defgroup   TLUP_ERROR_CODES_x  Error codes for TLVISA functions
\details 	Note: The instrument returns errors within the range -512 .. +1023. 
   The driver adds the value VI_INSTR_ERROR_OFFSET (0xBFFC0900). So the 
   driver returns instrument errors in the range 0xBFFC0700 .. 0xBFFC0CFF.
\ingroup    TLUP_MACROS_x
@{
*//*=========================================================================*/
// Offsets
#undef VI_INSTR_WARNING_OFFSET
#undef VI_INSTR_ERROR_OFFSET

#define VI_INSTR_WARNING_OFFSET        (0x3FFC0900L)
#define VI_INSTR_ERROR_OFFSET          (_VI_ERROR + VI_INSTR_WARNING_OFFSET)    ///< 0xBFFC0900L

//TODO usage isn't clear
#define TL_BAD_VAL_IN_BUFFER            777    ///< acquisition data bad value (0.0) in send buffer (for test only)
#define TL_SNH_ERROR                    666    ///< this is the error code for "should not happen"
#define TL_BAD_VAL_FROM_NVM             555    ///< acquisition data read bad value (0) from NVMEM
#define TL_BAD_VAL_FROM_DMA             444    ///< acquisition data read bad value from NVMEM not OK

// Driver errors
#define TL_INSTR_ERROR_NOT_SUPP_INTF   (VI_INSTR_ERROR_OFFSET + 0x01L)    ///< interface function isn't supported by this upSERIES type
#define TL_ERR_PARAMETER               (VI_INSTR_ERROR_OFFSET + 0x02L)    ///< error parsing a parameter
#define TL_ERR_P1_RANGE                (VI_INSTR_ERROR_OFFSET + 0x03L)    ///< parameter 1 out of range
#define TL_ERR_P2_RANGE                (VI_INSTR_ERROR_OFFSET + 0x04L)    ///< parameter 2 out of range
#define TL_ERR_P3_RANGE                (VI_INSTR_ERROR_OFFSET + 0x05L)    ///< parameter 3 out of range
#define TL_ERR_P4_RANGE                (VI_INSTR_ERROR_OFFSET + 0x06L)    ///< parameter 4 out of range
#define TL_ERR_P5_RANGE                (VI_INSTR_ERROR_OFFSET + 0x07L)    ///< parameter 5 out of range
#define TL_ERR_P6_RANGE                (VI_INSTR_ERROR_OFFSET + 0x08L)    ///< parameter 6 out of range
#define TL_ERR_P7_RANGE                (VI_INSTR_ERROR_OFFSET + 0x09L)    ///< parameter 7 out of range
#define TL_ERR_P8_RANGE                (VI_INSTR_ERROR_OFFSET + 0x0AL)    ///< parameter 8 out of range
#define TL_ERR_UNEXP_END               (VI_INSTR_ERROR_OFFSET + 0x0BL)    ///< unexpected end of command
#define TL_ERR_SERVICE                 (VI_INSTR_ERROR_OFFSET + 0x0CL)    ///< only allowed in service mode
#define TL_ERR_NOT_SVC                 (VI_INSTR_ERROR_OFFSET + 0x0DL)    ///< not allowed in service mode
#define TL_ERR_ADJ_MATH                (VI_INSTR_ERROR_OFFSET + 0x0EL)    ///< error during adjustment coefficient calculations, e.g. division by (almost) zero
#define TL_ERR_ADJ_INVAL               (VI_INSTR_ERROR_OFFSET + 0x0FL)    ///< invalid adjustment data set, e.g. wrong method stored in data set

#define TL_ERR_HAL_ERR                 (VI_INSTR_ERROR_OFFSET + 0x10L)    ///< hardware abstraction layer error
#define TL_ERR_HAL_BUSY                (VI_INSTR_ERROR_OFFSET + 0x11L)    ///< hardware abstraction layer busy
#define TL_ERR_HAL_TIMO                (VI_INSTR_ERROR_OFFSET + 0x12L)    ///< hardware abstraction layer timeout
#define TL_MATH_RANGE                  (VI_INSTR_ERROR_OFFSET + 0x13L)    ///< a conversion string --> float/integer failed due to out of range
#define TL_ERR_USB                     (VI_INSTR_ERROR_OFFSET + 0x14L)    ///< error in an USB library function
#define TL_ERR_NOT_AUTH                (VI_INSTR_ERROR_OFFSET + 0x15L)    ///< not authenticated, permission denied
#define TL_ERR_AUTH_FAIL               (VI_INSTR_ERROR_OFFSET + 0x16L)    ///< attempt to get authenticated failed
#define TL_ERR_NO_TIME_SET             (VI_INSTR_ERROR_OFFSET + 0x17L)    ///< RTC time needed but not yet set
#define TL_ERR_RTOS                    (VI_INSTR_ERROR_OFFSET + 0x18L)    ///< error from RTOS, e.g. start of thread failed, creation of mutex failed

#define TL_ERR_INVAL_ATTR              (VI_INSTR_ERROR_OFFSET + 0x19L)    ///< error invalid attribute
#define TL_ERR_INVAL_RESPONSE    	   (VI_INSTR_ERROR_OFFSET + 0x1AL)    ///< error invalid response from device
#define TL_ERR_INVAL_PARAM_RESPONSE    (VI_INSTR_ERROR_OFFSET + 0x1BL)    ///< error invalid parameter response from device

// upTEMP
#define TL_ERR_TEMP_INVAL              (VI_INSTR_ERROR_OFFSET + 0x1EL)    ///< UP-TEMP specific: temperature measurement was invalid
#define TL_ERR_TEMP_HARD_FAULT         (VI_INSTR_ERROR_OFFSET + 0x1FL)    ///< UP-TEMP specific: temperature measurement had a hard fault, e.g. open or short RTD or Rsense
#define TL_ERR_TEMP_ADC_HARD           (VI_INSTR_ERROR_OFFSET + 0x20L)    ///< UP-TEMP specific: temperature measurement had a bad ADC reading, e.g. due to large external noise
#define TL_ERR_TEMP_CJ_HARD            (VI_INSTR_ERROR_OFFSET + 0x21L)    ///< UP-TEMP specific: temperature measurement was invalid due to cold junction hard error
#define TL_ERR_TEMP_CJ_SOFT            (VI_INSTR_ERROR_OFFSET + 0x22L)    ///< UP-TEMP specific: temperature measurement was beyond normal range
#define TL_ERR_TEMP_OVER               (VI_INSTR_ERROR_OFFSET + 0x23L)    ///< UP-TEMP specific: temperature measurement was over or under limit
#define TL_ERR_TEMP_ADC_SOFT           (VI_INSTR_ERROR_OFFSET + 0x24L)    ///< UP-TEMP specific: temperature measurement ADC input was beyond rated range
#define TL_ERR_TEMP_INVAL_CHAN         (VI_INSTR_ERROR_OFFSET + 0x25L)    ///< UP-TEMP specific: temperature measurement invalid channel number
#define TL_ERR_TEMP_INVAL_POINT        (VI_INSTR_ERROR_OFFSET + 0x26L)    ///< UP-TEMP specific: temperature measurement invalid point number

#define TL_ERR_NVM_BOOT                (VI_INSTR_ERROR_OFFSET + 0x28L)    ///< error during boot, cannot read NVMEM
#define TL_ERR_NVM_NEW                 (VI_INSTR_ERROR_OFFSET + 0x29L)    ///< not really an error, NVMEM was empty at boot time
#define TL_ERR_NVM_CHKSUM              (VI_INSTR_ERROR_OFFSET + 0x2AL)    ///< checksum error on read of NVMEM
#define TL_ERR_DAC_RANGE               (VI_INSTR_ERROR_OFFSET + 0x32L)    ///< DAC value out of range
#define TL_ERR_ADC_RANGE               (VI_INSTR_ERROR_OFFSET + 0x33L)    ///< ADC value out of range
#define TL_ERR_BUF_OVL                 (VI_INSTR_ERROR_OFFSET + 0x3CL)    ///< buffer overflow
#define TL_ERR_BUF_UVL                 (VI_INSTR_ERROR_OFFSET + 0x3DL)    ///< buffer underflow
#define TL_ERR_CMD_BUF_OVL             (VI_INSTR_ERROR_OFFSET + 0x3EL)    ///< command buffer overflow
#define TL_ERR_NOT_IDLE                (VI_INSTR_ERROR_OFFSET + 0x41L)    ///< only allowed in idle mode

// upTEMP - Flash
#define TL_ERR_F_CORRUPT               (VI_INSTR_ERROR_OFFSET + 0x46L)    ///< data set or sector corrupt, i.e. checksum does not match
#define TL_ERR_F_MEMFULL               (VI_INSTR_ERROR_OFFSET + 0x47L)    ///< flash check returned 'all sectors full'
#define TL_ERR_F_ORPHAN                (VI_INSTR_ERROR_OFFSET + 0x48L)    ///< data set with no predecessor and no successor but not the only data set
#define TL_ERR_F_OPEN                  (VI_INSTR_ERROR_OFFSET + 0x49L)    ///< more than one open data set detected
#define TL_ERR_DS_UNINIT               (VI_INSTR_ERROR_OFFSET + 0x4AL)    ///< attempt to write a data point although no open data set
#define TL_ERR_F_NO_FILE               (VI_INSTR_ERROR_OFFSET + 0x4BL)    ///< attempt to delete a data set but no data set available to delete
#define TL_ERR_F_NO_SUC                (VI_INSTR_ERROR_OFFSET + 0x4CL)    ///< after deleting data set no successor or predecessor found but should have one
#define TL_ERR_SECT_FULL               (VI_INSTR_ERROR_OFFSET + 0x4DL)    ///< sector full, no 'next write address' found
#define TL_ERR_TOO_MUCH_DATASETS       (VI_INSTR_ERROR_OFFSET + 0x4EL)    ///< too much data sets (index of directory of data sets is too high)

#define TL_ERR_RANGE                   (VI_INSTR_ERROR_OFFSET + 0x50L)    ///< error checking range value

#define TL_ERR_ADJUST                  (VI_INSTR_ERROR_OFFSET + 0x5AL)    ///< error checking adjust value

#define TL_ERR_SETUP                   (VI_INSTR_ERROR_OFFSET + 0x64L)    ///< error checking setup value

// upLED
#define TL_ERR_OW_TIMO                 (VI_INSTR_ERROR_OFFSET + 0x6FL)    ///< a timeout on the 1wire bus occurred
#define TL_ERR_NO_LED                  (VI_INSTR_ERROR_OFFSET + 0x70L)    ///< no LED detected via OWB
#define TL_ERR_OTP               	   (VI_INSTR_ERROR_OFFSET + 0x71L)    ///< attempt to switch ON LED cancelled due to over temperature
#define TL_ERR_NO_VCC             	   (VI_INSTR_ERROR_OFFSET + 0x72L)    ///< no power supply detected (12 V) - needed for LED ON

// Driver warnings
#undef VI_INSTR_WARN_OVERFLOW
#undef VI_INSTR_WARN_UNDERRUN
#undef VI_INSTR_WARN_NAN

#define VI_INSTR_WARN_OVERFLOW         (VI_INSTR_WARNING_OFFSET + 0x01L)   /* 3FFC0901, 1073481985 */
#define VI_INSTR_WARN_UNDERRUN         (VI_INSTR_WARNING_OFFSET + 0x02L)   /* 3FFC0902, 1073481986 */
#define VI_INSTR_WARN_NAN              (VI_INSTR_WARNING_OFFSET + 0x03L)   /* 3FFC0903, 1073481987 */
/**@}*/  /* TLUP_ERROR_CODES_x */

/*========================================================================*//**
\defgroup   TLUP_ATTR_x  Attributes
\ingroup    TLUP_MACROS_x
@{
*//*=========================================================================*/
#define TLUP_ATTR_SET_VAL           (0)
#define TLUP_ATTR_MIN_VAL           (1)
#define TLUP_ATTR_MAX_VAL           (2)
#define TLUP_ATTR_DFLT_VAL          (3)
/**@}*/  /* TLUP_ATTR_x */ 


/*========================================================================*//**
\defgroup   TLUP_TEMP_x  Temperature never measured value
\ingroup    TLUP_MACROS_x
@{
*//*=========================================================================*/
#define TEMP_NEVER_MEASURED_VALUE      (NAN)   ///< 'temperature' that will be returned when selected channel never was measured before
/**@}*/  /* TLUP_TEMP_x */


/*========================================================================*//**
\defgroup   TLUP_METHODS_x Functions
\ingroup    TLUP_x
\brief      Functions provided by TLVISA library, e.g. communicating with devices.
@{
*//*=========================================================================*/   
TLUP_API ViStatus _VI_FUNC TLUP_init (ViRsrc resourceName, ViBoolean IDQuery, ViBoolean resetDevice, ViPSession instrumentHandle);
TLUP_API ViStatus _VI_FUNC TLUP_close (ViSession instrumentHandle);

/*========================================================================*//**
\defgroup   TLUP_METHODS_RM_x Resource Manager TLVISA library functions
\ingroup    TLUP_METHODS_x
\brief      Functions provided by TLVISA library for managing resources, e.g. finding resources.
@{
*//*=========================================================================*/
TLUP_API ViStatus _VI_FUNC TLUP_findRsrc (ViSession instrumentHandle, ViPUInt32 resourceCount);
TLUP_API ViStatus _VI_FUNC TLUP_getRsrcName (ViSession instrumentHandle, ViUInt32 index, ViChar _VI_FAR resourceName[]);
TLUP_API ViStatus _VI_FUNC TLUP_getRsrcInfo (ViSession instrumentHandle, ViUInt32 index, ViChar _VI_FAR modelName[], ViChar _VI_FAR serialNumber[], ViChar _VI_FAR manufacturer[], ViPBoolean resourceAvailable);
/**@}*/  /* TLUP_METHODS_RM_x */


/*========================================================================*//**
\defgroup   TLUP_METHODS_SYSTEM_x System Functions
\ingroup    TLUP_METHODS_x
\brief      The System class groups functions for general system level control.
@{
*//*=========================================================================*/

	/*========================================================================*//**
	\defgroup   TLUP_METHODS_SYSTEM_TEMP_UNIT_x System Temperature Unit Functions
	\ingroup    TLUP_METHODS_SYSTEM_x
	\brief      System temperature unit.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_setTempUnit (ViSession instrumentHandle, ViUInt16  temperatureUnit);

		/*========================================================================*//**
		\defgroup   TLUP_SYSTEM_TEMP_UNIT_FLAGS_x System Temperature Unit Flags
		\ingroup    TLUP_MACROS_x
		@{
		*//*=========================================================================*/
        #define TLUP_TEMP_U_KELVIN  (0) ///< temperature unit Kelvin
		#define TLUP_TEMP_U_CELSIUS (1) ///< temperature unit grad celsius
		#define TLUP_TEMP_U_FAHREN	(2) ///< temperature unit grad fahrenheit
		/**@}*/  /* TLUP_SYSTEM_TEMP_UNIT_FLAGS_x */

    TLUP_API ViStatus _VI_FUNC TLUP_getTempUnit (ViSession instrumentHandle, ViPUInt16 temperatureUnit);
	/**@}*/  /* TLUP_METHODS_SYSTEM_TEMP_UNIT_x */
	
	
	/*========================================================================*//**
	\defgroup   TLUP_METHODS_SYSTEM_DATE_TIME_x System Date Time Functions
	\ingroup    TLUP_METHODS_SYSTEM_x
	\brief      System date and time control.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_setTimeAndDate (ViSession instrumentHandle, ViUInt16 year, ViUInt16 month, ViUInt16 day, ViUInt16 hour, ViUInt16 minute, ViUInt16 second);
    TLUP_API ViStatus _VI_FUNC TLUP_getTimeAndDate (ViSession instrumentHandle, ViPUInt16 year, ViPUInt16 month, ViPUInt16 day, ViPUInt16 hour, ViPUInt16 minute, ViPUInt16 second);
	/**@}*/  /* TLUP_METHODS_SYSTEM_DATE_TIME_x */  

	/*========================================================================*//**
	\defgroup   TLUP_METHODS_SYSTEM_LINE_FREQUENCY_REJECTION_x System Line Frequency Rejection Functions
	\ingroup    TLUP_METHODS_SYSTEM_x
	\brief      Line frequency rejection setup.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_setLineFreqReject (ViSession instrumentHandle, ViUInt16  lineErequencyRejection);
    TLUP_API ViStatus _VI_FUNC TLUP_getLineFreqReject (ViSession instrumentHandle, ViPUInt16 lineFrequencyRejection);

		/*========================================================================*//**
		\defgroup   TLUP_LINE_FREQUENCY_REJECTION_FLAGS_x System Line Frequency Rejection Flags
		\ingroup    TLUP_MACROS_x
		@{
		*//*=========================================================================*/
		#define TLUP_LINE_FREQ_REJECT_ALL  (0) ///< line frequency rejection 
		#define TLUP_LINE_FREQ_REJECT_50   (1) ///< line frequency rejection
		#define TLUP_LINE_FREQ_REJECT_60   (2) ///< line frequency rejection
		/**@}*/  /* TLUP_LINE_FREQUENCY_REJECTION_FLAGS_x */ 

	/**@}*/  /* TLUP_METHODS_SYSTEM_LINE_FREQUENCY_REJECTION_x */  
	
	
	/*========================================================================*//**
	\defgroup   TLUP_METHODS_SYSTEM_LED_INFO_x System LED Head Functions
	\ingroup    TLUP_METHODS_SYSTEM_x
	\brief      LED head data.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_getLedInfo (ViSession instrumentHandle, ViChar _VI_FAR ledName[], ViChar _VI_FAR ledSerialNumber[], ViPReal64 ledCurrentLimit, ViPReal64 ledForwardVoltage, ViPReal64 ledWavelength);
	/**@}*/  /* TLUP_METHODS_SYSTEM_LED_INFO_x */ 
			

	/*========================================================================*//**
	\defgroup   TLUP_METHODS_SYSTEM_LOG_INFO_x System Log Message
	\ingroup    TLUP_METHODS_SYSTEM_x
	\brief      System Log Message.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_getLogMessage (ViSession instrumentHandle, ViChar _VI_FAR logMessage[]);
	/**@}*/  /* TLUP_METHODS_SYSTEM_LOG_INFO_x */


//    /*========================================================================*//**
//    \defgroup   TLUP_METHODS_SYSTEM_OP_MODE_x System Operating Mode
//    \ingroup    TLUP_METHODS_SYSTEM_x
//    \brief      Get System Operating Mode.
//    @{
//    *//*=========================================================================*/
//    TLUP_API ViStatus _VI_FUNC TLUP_getOpMode (ViSession instr, ViPInt32  pOpModeFlag, ViChar _VI_FAR opMode[]);
//
//        /*========================================================================*//**
//        \defgroup   TLUP_OPERATING_MODE_FLAGS_x upLED System Operating Mode Flags
//        \ingroup    TLUP_MACROS_x
//        @{
//        *//*=========================================================================*/
//        #define TLUP_OPERATING_MODE_POWERON      0x01 ///< upLED operating mode 'power on'
//        #define TLUP_OPERATING_MODE_NOLED_NOVCC  0x02 ///< upLED operating mode 'no Vcc no LED'
//        #define TLUP_OPERATING_MODE_NOLED_VCCOK  0x03 ///< upLED operating mode  no LED but VccOK'
//        #define TLUP_OPERATING_MODE_CON_NOVCC    0x04 ///< upLED operating mode 'LED connected, not yet read out, no Vcc'
//        #define TLUP_OPERATING_MODE_CON_VCCOK    0x05 ///< upLED operating mode 'LED connected, not yet read out, VccOK'
//        #define TLUP_OPERATING_MODE_LED_NOVCC    0x06 ///< upLED operating mode 'LED connected, read out, no Vcc'
//        #define TLUP_OPERATING_MODE_LED_OFF      0x07 ///< upLED operating mode 'LED connected, read out, DAC=0, VccOK'
//        #define TLUP_OPERATING_MODE_ON_POTI      0x08 ///< upLED operating mode 'ON', LED connected, read out, DAC!=0 last new value got from Poti, VccOK,
//        #define TLUP_OPERATING_MODE_ON_REM       0x09 ///< upLED operating mode 'ON', LED connected, read out, DAC!=0 last new value got from Interface, VccOK,
//        #define TLUP_OPERATING_MODE_ON_NVMEM     0x0A ///< upLED operating mode 'ON', LED connected, read out, DAC!=0 last new value got from NVMEM, VccOK,
//        #define TLUP_OPERATING_MODE_SERVICE      0x0B ///< upLED operating mode 'SERVICE', no automated set of DAC etc. waiting for remote commands
//        #define TLUP_OPERATING_MODE_ON_PROBE     0x0C ///< upLED operating mode 'testwise ON' to check for non Thorlabs LED
//        /**@}*/  /* TLUP_OPERATING_MODE_FLAGS_x */
//    /**@}*/  /* TLUP_METHODS_SYSTEM_OP_MODE_x */


    /*========================================================================*//**
	\defgroup   TLUP_METHODS_SYSTEM_UPLED_x upLED System
	\ingroup    TLUP_METHODS_SYSTEM_x
	\brief      Corresponds to upLED System.
	@{
	*//*=========================================================================*/
        /*========================================================================*//**
        \defgroup   TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_x upLED System - Operation Mode
        \ingroup    TLUP_METHODS_SYSTEM_UPLED_x
        \brief      Actual upLED System Operation Mode.
        @{
        *//*=========================================================================*/
            /*========================================================================*//**
            \defgroup   TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_METHODS_x upLED System - Operation Mode - Methods
            \ingroup    TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_x
            \brief      upLED System Operation Mode methods.
            @{
            *//*=========================================================================*/
                /*========================================================================*//**
                \defgroup   TLUP_MACROS_UPLED_x upLED System - Macros
                \ingroup    TLUP_MACROS_x
                @{
                *//*=========================================================================*/
                    /*========================================================================*//**
                    \defgroup   TLUP_MACROS_UPLED_OPERATION_MODE_x upLED System - Macros - Operation Mode
                    \ingroup    TLUP_MACROS_UPLED_x
                    @{
                    *//*=========================================================================*/
                        /*========================================================================*//**
                        \defgroup   TLUP_MACROS_UPLED_OPERATION_MODE_OP_MODE_STATES_x upLED System - Macros - Operation Mode - opMode
                        \ingroup    TLUP_MACROS_UPLED_OPERATION_MODE_x
                        @{
                        *//*=========================================================================*/
        #define TLUP_OPERATION_MODE_opMode_UNSPECIFIED     (0x00)
        #define TLUP_OPERATION_MODE_opMode_PON             (0x01) ///< upLED operating mode 'power on'
        #define TLUP_OPERATION_MODE_opMode_NoLED_NoVcc     (0x02) ///< upLED operating mode 'no Vcc no LED'
        #define TLUP_OPERATION_MODE_opMode_NoLED_VccOK     (0x03) ///< upLED operating mode  no LED but VccOK'
        #define TLUP_OPERATION_MODE_opMode_CON_NoVcc       (0x04) ///< upLED operating mode 'LED connected, not yet read out, no Vcc'
        #define TLUP_OPERATION_MODE_opMode_CON_VccOK       (0x05) ///< upLED operating mode 'LED connected, not yet read out, VccOK'
        #define TLUP_OPERATION_MODE_opMode_LED_NoVcc       (0x06) ///< upLED operating mode 'LED connected, read out, no Vcc'
        #define TLUP_OPERATION_MODE_opMode_LED_OFF         (0x07) ///< upLED operating mode 'LED connected, read out, DAC=0, VccOK'
        #define TLUP_OPERATION_MODE_opMode_ON_POTI         (0x08) ///< upLED operating mode 'ON, LED connected, read out, DAC!=0 last new value got from Poti, VccOK'
        #define TLUP_OPERATION_MODE_opMode_ON_REM          (0x09) ///< upLED operating mode 'ON, LED connected, read out, DAC!=0 last new value got from Interface, VccOK'
        #define TLUP_OPERATION_MODE_opMode_ON_NVMEM        (0x0A) ///< upLED operating mode 'ON, LED connected, read out, DAC!=0 last new value got from NVMEM, VccOK'
        #define TLUP_OPERATION_MODE_opMode_Service         (0x0B) ///< upLED operating mode 'SERVICE, no automated set of DAC etc. waiting for remote commands'
        #define TLUP_OPERATION_MODE_opMode_ON_Probe        (0x0C) ///< upLED operating mode 'testwise ON to check for non Thorlabs LED'
                        /**@}*/  /* TLUP_MACROS_UPLED_OPERATION_MODE_OP_MODE_STATES_x */
                    /**@}*/  /* TLUP_MACROS_UPLED_OPERATION_MODE_x */
                /**@}*/  /* TLUP_MACROS_UPLED_x */
                
                /*========================================================================*//**
                \defgroup   TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_STATE_x upLED System - Operation Mode - Method
                \ingroup    TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_METHODS_x
                \brief      Get upLED System - Operation Mode - State.
                @{
                **//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_getOpMode (ViSession instr, ViPUInt32  pOpModeFlag, ViChar _VI_FAR opMode[]);
                /**@}*/  /* TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_STATE_x */
                
                /*========================================================================*//**
                \defgroup   TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_REGISTER_x upLED System - Operation Mode - Extended - Method
                \ingroup    TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_METHODS_x
                \brief      Get upLED System - Operation Mode - Extended State.
                @{
                **//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_getExtendedOperationModes (ViSession instr, ViUInt8 _VI_FAR extendedOperationModes[]);

                    /*========================================================================*//**
                    \defgroup   TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_DEFINITIONS_x upLED System - Macros - Operation Mode - Extended - Definitions
                    \ingroup    TLUP_MACROS_UPLED_x
                    @{
                    *//*=========================================================================*/
        #define TLUP_OPERATION_MODE_ARRAY_LENGTH   (32)
        #define TLUP_OPERATION_MODE_isSet          (0xFF)
        #define TLUP_OPERATION_MODE_isNotSet       (0x00)
                    /**@}*/  /* TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_DEFINITIONS_x */

                    /*========================================================================*//**
                    \defgroup   TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_STATES_x upLED System - Macros - Operation Mode - Extended - States Map
                    \ingroup    TLUP_MACROS_UPLED_x
                    @{
                    *//*=========================================================================*/
        #define TLUP_OPERATION_MODE_RUN            (0x00)
        #define TLUP_OPERATION_MODE_ENA            (0x01)
        #define TLUP_OPERATION_MODE_OWB_DET        (0x02)
        #define TLUP_OPERATION_MODE_OWB_OK         (0x03)
        #define TLUP_OPERATION_MODE_VCC_ERR        (0x04)
        #define TLUP_OPERATION_MODE_E_VCC_ERR      (0x05)
        #define TLUP_OPERATION_MODE_OTP            (0x06)
        #define TLUP_OPERATION_MODE_E_OTP          (0x07)
        #define TLUP_OPERATION_MODE_LED_ERR        (0x08)
        #define TLUP_OPERATION_MODE_OPEN           (0x09)
        #define TLUP_OPERATION_MODE_NON_THOR_LED   (0x0A)   ///< Is set if non Thorlabs LEDs are enabled
        #define TLUP_OPERATION_MODE_RECON          (0x0B)
        #define TLUP_OPERATION_MODE_PON            (0x0C)
        #define TLUP_OPERATION_MODE_START_ERR      (0x0D)
        #define TLUP_OPERATION_MODE_LED_PRESENT    (0x0E)
        #define TLUP_OPERATION_MODE_E_POTI         (0x0F)
        #define TLUP_OPERATION_MODE_BUCK           (0x10)
        #define TLUP_OPERATION_MODE_NO_LED         (0x11)
        #define TLUP_OPERATION_MODE_ISRC           (0x12)   ///< Current Set Point Source
        #define TLUP_OPERATION_MODE_OP_MODE        (0x13)   ///< System Operating Mode
        #define TLUP_OPERATION_MODE_SERVICE        (0x14)   ///< Is set if Device is in Service Mode
        #define TLUP_OPERATION_MODE_AUTH           (0x15)   ///< Authorized Access Level
        #define TLUP_OPERATION_MODE_RESERVED       (0x16)   ///< Reserved for later use
        #define TLUP_OPERATION_MODE_LIST_END       (0x1F)   ///< Marks the end of the enumeration list

                        /*========================================================================*//**
                        \defgroup   TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_STATES_ISRC_x upLED System - Macros - Operation Mode - Extended - ISRC States
                        \ingroup    TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_STATES_x
                        @{
                        *//*=========================================================================*/
            #define TLUP_OPERATION_MODE_ISRC_UNSPECIFIED       (0x00)
            #define TLUP_OPERATION_MODE_ISRC_POTI              (0x01)
            #define TLUP_OPERATION_MODE_ISRC_REM               (0x02)
            #define TLUP_OPERATION_MODE_ISRC_FIX               (0x03)
                        /**@}*/  /* TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_STATES_ISRC_x */

                        /*========================================================================*//**
                        \defgroup   TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_STATES_AUTH_x upLED System - Macros - Operating Mode - Extended - Authentication States
                        \ingroup    TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_STATES_x
                        @{
                        *//*=========================================================================*/
            #define TLUP_OPERATION_MODE_AUTH_NONE              (0x00)
            #define TLUP_OPERATION_MODE_AUTH_Calibration       (0x01)
            #define TLUP_OPERATION_MODE_AUTH_Adjustment        (0x02)
            #define TLUP_OPERATION_MODE_AUTH_Device            (0x04)
                        /**@}*/  /* TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_STATES_AUTH_x */
                    /**@}*/  /* TLUP_MACROS_UPLED_OPERATION_MODE_REGISTER_STATES_x */
                /**@}*/  /* TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_REGISTER_x */
            /**@}*/  /* TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_METHODS_x */
        /**@}*/  /* TLUP_METHODS_SYSTEM_UPLED_OPERATION_MODE_x */
    /**@}*/  /* TLUP_METHODS_SYSTEM_UPLED_x */

	/*========================================================================*//**
	\defgroup   TLUP_METHODS_SYSTEM_SAVE_TO_NVMEM_x Save values into NVMEM
	\ingroup    TLUP_METHODS_SYSTEM_x
	\brief      Save values of type group into NVMEM.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_saveToNVMEM (ViSession instrumentHandle, ViUInt16 group);

		/*========================================================================*//**
		\defgroup   TLUP_SAVE_TO_NVMEM_FLAGS_x Save values into NVMEM Flags
		\ingroup    TLUP_MACROS_x
		@{
		*//*=========================================================================*/
		#define TLUP_SAVE_TO_NVMEM_ALL  		(0) ///< save to NVMEM all
		#define TLUP_SAVE_TO_NVMEM_LED_OPM  	(1) ///< save to NVMEM LED operating mode
		#define TLUP_SAVE_TO_NVMEM_LED_CURR 	(2) ///< save to NVMEM LED currents Imax. and Iset_nvmem
		#define TLUP_SAVE_TO_NVMEM_TEC_SETUP  	(3) ///< save to NVMEM TEC user setup
		#define TLUP_SAVE_TO_NVMEM_TEMP_CHAN    (4) ///< save to NVMEM TEMP channel list
		#define TLUP_SAVE_TO_NVMEM_TEMP_SENS	(5) ///< save to NVMEM TEMP sensor parameters
		#define TLUP_SAVE_TO_NVMEM_TEMP_CONF  	(6) ///< save to NVMEM TEMP configuration
		#define TLUP_SAVE_TO_NVMEM_TEMP_NEXT  	(7) ///< save to NVMEM TEMP next data set configuration
		/**@}*/  /* TLUP_SAVE_TO_NVMEM_FLAGS_x */
	/**@}*/  /* TLUP_METHODS_SYSTEM_SAVE_TO_NVMEM_x */

/**@}*/  /* TLUP_METHODS_SYSTEM_x */ 



/*========================================================================*//**
\defgroup   TLUP_METHODS_MEASURE_x Measure Functions
\ingroup    TLUP_METHODS_x
\brief      This class of functions transfers measurement data from the instrument.
@{
*//*=========================================================================*/
  
	/*========================================================================*//**
	\defgroup   TLUP_METHODS_MEASURE_READ_x Measure Read Functions
	\ingroup    TLUP_METHODS_MEASURE_x
	\brief      The Read class contains functions to read measurement results from the instrument.
	@{
	*//*=========================================================================*/ 
    TLUP_API ViStatus _VI_FUNC TLUP_measDeviceTemperature (ViSession instrumentHandle, ViPReal64 deviceTemperature);
    TLUP_API ViStatus _VI_FUNC TLUP_measSupplyVoltage (ViSession instrumentHandle, ViPReal64 supplyVoltage);
	
	/*========================================================================*//**
	\defgroup   TLUP_METHODS_MEASURE_READ_LED_x Measure Read Functions
	\ingroup    TLUP_METHODS_MEASURE_READ_x
	\brief      The Read class contains functions to read measurement results from the LED instrument.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_measureLedCurrent (ViSession instrumentHandle, ViPReal64 ledCurrent);
    TLUP_API ViStatus _VI_FUNC TLUP_measureLedVoltage (ViSession instrumentHandle, ViPReal64 ledVoltage);
    TLUP_API ViStatus _VI_FUNC TLUP_measurePotiValue (ViSession instrumentHandle, ViPReal64 potiValue);
	/**@}*/  /* TLUP_METHODS_MEASURE_LED_x */
	
	/*========================================================================*//**
	\defgroup   TLUP_METHODS_MEASURE_READ_TEC_x Measure Read Functions
	\ingroup    TLUP_METHODS_MEASURE_READ_x
	\brief      The Read class contains functions to read measurement results from the TEC instrument.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_measTecTemperature (ViSession instrumentHandle, ViPReal64 tecTemperature);
    TLUP_API ViStatus _VI_FUNC TLUP_measTecCurrent (ViSession instrumentHandle, ViPReal64 tecCurrent);
    TLUP_API ViStatus _VI_FUNC TLUP_measTecVoltage (ViSession instrumentHandle, ViPReal64 tecVoltage);
	/**@}*/  /* TLUP_METHODS_MEASURE_TEC_x */
	
	/*========================================================================*//**
	\defgroup   TLUP_METHODS_MEASURE_READ_TEMP_x Measure Read Functions
	\ingroup    TLUP_METHODS_MEASURE_READ_x
	\brief      The Read class contains functions to read measurement results from the TEMP instrument.
	@{
	*//*=========================================================================*/
    TLUP_API ViStatus _VI_FUNC TLUP_measTempTemperature (ViSession instrumentHandle, ViUInt8 temperatureChannel, ViPReal64 temperature, ViPBoolean pIsNew);
    TLUP_API ViStatus _VI_FUNC TLUP_measTempTemperatureAll (ViSession instrumentHandle, ViReal64 measurementValues[], ViPBoolean pIsNew);
    TLUP_API ViStatus _VI_FUNC TLUP_measTempTemperature_RAW_All (ViSession instrumentHandle, ViReal64 measurementValues[], ViPBoolean pIsNew);

		/*========================================================================*//**
		\defgroup   TLUP_METHODS_MEASURE_READFLAGS_x Read measurement results Flags
		\ingroup    TLUP_MACROS_x
		@{
		*//*=========================================================================*/
		#define TLUP_TEMP_DATA_OLD  (0) ///< temperature data is old (already read out or not yet measured)
		#define TLUP_TEMP_DATA_NEW  (1)	///< temperature data is new measured (not yet read out)
		/**@}*/  /* TLUP_METHODS_MEASURE_READ_FLAGS_x */
	/**@}*/  /* TLUP_METHODS_MEASURE_TEMP_x */
	
/**@}*/  /* TLUP_METHODS_MEASURE_x */ 




 /*========================================================================*//**
\defgroup   TLUP_METHODS_SOURCE_x Source Functions
\ingroup    TLUP_METHODS_x
\brief      This class of functions are instrument specific functions.
@{
*//*=========================================================================*/

  /*========================================================================*//**
	\defgroup   TLUP_METHODS_SOURCE_ACTION_x Source Action Functions
	\ingroup    TLUP_METHODS_SOURCE_x
	\brief      This class of functions are instrument specific action functions
	@{
	*//*=========================================================================*/

	   /*========================================================================*//**
		\defgroup   TLUP_METHODS_SOURCE_ACTION_LED_x Source Action Functions
		\ingroup    TLUP_METHODS_SOURCE_ACTION_x
		\brief      This class of functions are LED instrument specific action functions
		@{
		*//*=========================================================================*/
        TLUP_API ViStatus _VI_FUNC TLUP_switchLedOutput (ViSession instrumentHandle, ViBoolean ledOutput);
        TLUP_API ViStatus _VI_FUNC TLUP_getLedOutputState (ViSession instrumentHandle, ViPBoolean ledOutput);
		/**@}*/  /* TLUP_METHODS_SOURCE_ACTION_LED_x */

	   /*========================================================================*//**
		\defgroup   TLUP_METHODS_SOURCE_ACTION_TEC_x Source Action Functions
		\ingroup    TLUP_METHODS_SOURCE_ACTION_x
		\brief      This class of functions are TEC instrument specific action functions
		@{
		*//*=========================================================================*/
        TLUP_API ViStatus _VI_FUNC TLUP_switchTecOutput (ViSession instrumentHandle, ViBoolean tecOutput);
        TLUP_API ViStatus _VI_FUNC TLUP_getTecOutputState (ViSession instrumentHandle, ViPBoolean tecOutput);
		/**@}*/  /* TLUP_METHODS_SOURCE_ACTION_TEC_x */

	   /*========================================================================*//**
		\defgroup   TLUP_METHODS_SOURCE_ACTION_TEMP_x Source Action Functions
		\ingroup    TLUP_METHODS_SOURCE_ACTION_x
		\brief      This class of functions are TEMP instrument specific action functions
		@{
		*//*=========================================================================*/
        TLUP_API ViStatus _VI_FUNC TLUP_setTempMeasurementState (ViSession instrumentHandle, ViUInt16 tempMeasurementState);
        TLUP_API ViStatus _VI_FUNC TLUP_getTempMeasurementState (ViSession instrumentHandle, ViPUInt16 tempMeasurementState);
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_ACTION_TEMP_FLAGS_x Source TEMP Measurement State Flags
			\ingroup    TLUP_MACROS_x
			@{
			*//*=========================================================================*/
			#define TLUP_TEMP_MEAS_STATE_IDLE  	(0) ///< TEMP measurement state 'idle' i.e. no Temp. measurements shall be taken
			#define TLUP_TEMP_MEAS_STATE_MEAS 	(1) ///< TEMP measurement state 'measure' i.e. do measurements according to channel list as fast as possible in a loop
			#define TLUP_TEMP_MEAS_STATE_LOG 	(2) ///< TEMP measurement state 'log' i.e. do measurements according to channel list and save them in wait time interval
			/**@}*/  /* TLUP_METHODS_SOURCE_ACTION_TEMP_FLAGS_x */

		/**@}*/  /* TLUP_METHODS_SOURCE_ACTION_TEMP_x */
		
	/**@}*/  /* TLUP_METHODS_SOURCE_ACTION_x */


  /*========================================================================*//**
	\defgroup   TLUP_METHODS_SOURCE_CONFIG_x Source Config Functions
	\ingroup    TLUP_METHODS_SOURCE_x
	\brief      This class of functions are instrument specific configuration functions
	@{
	*//*=========================================================================*/

	   /*========================================================================*//**
		\defgroup   TLUP_METHODS_SOURCE_CONFIG_LED_x Source Config Functions
		\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
		\brief      This class of functions are LED instrument specific configuration functions
		@{
		*//*=========================================================================*/
		
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_LED_CURR_LIM_USER_x Source User Current Limit (may be saved into NVMEM)
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are LED instrument specific user current limit (may be saved into NVMEM)
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setLedCurrentLimitUser (ViSession instrumentHandle, ViReal64 LEDCurrentLimitUser);
            TLUP_API ViStatus _VI_FUNC TLUP_getLedCurrentLimitUser (ViSession instrumentHandle, ViInt16 Attribute, ViPReal64 LEDCurrentLimitUser);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_LED_CURR_LIM_USER_x */
			
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_LED_CURR_SET_STARTUP_x Source User Current Setpoint Startup for/from NVMEM Config Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are LED instrument specific user current setpoint startup for/from NVMEM configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setLedCurrentSetpointStartup (ViSession instrumentHandle, ViReal64 LEDCurrentSetUser);
            TLUP_API ViStatus _VI_FUNC TLUP_getLedCurrentSetpointStartup (ViSession instrumentHandle, ViInt16 Attribute, ViPReal64 LEDCurrentSetUser);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_LED_CURR_SET_USER_x */
			
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_LED_CURR_SET_x Source Current Setpoint Config Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are LED instrument specific current setpoint configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setLedCurrentSetpoint (ViSession instrumentHandle, ViReal64 LEDCurrentSetpoint);
            TLUP_API ViStatus _VI_FUNC TLUP_getLedCurrentSetpoint (ViSession instrumentHandle, ViInt16 Attribute, ViPReal64 LEDCurrentSetpoint);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_LED_CURR_SET_x */
		
		
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_LED_CURR_SET_x Source Config Set Current Source Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are LED instrument set current source functions
			@{
			*//*=========================================================================*/	
            TLUP_API ViStatus _VI_FUNC TLUP_setLedCurrentSetpointSource (ViSession instrumentHandle, ViUInt16 currentSetSource);
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_LED_CURR_SET_FLAGS_x Source Config Set Current Source Flags
				\ingroup    TLUP_MACROS_x
				@{
				*//*=========================================================================*/
				#define TLUP_LED_SOUR_ISET_POTI  	(0) ///< Potentiometer value is the source of the current setpoint
				#define TLUP_LED_SOUR_ISET_NVMEM 	(1) ///< LED device driver NVMEM is the source of the current setpoint
				#define TLUP_LED_SOUR_ISET_REMOTE 	(2) ///< Remote input the source of the current setpoint (device is waiting for that value)
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_LED_CURR_SET_FLAGS_x */
				
            TLUP_API ViStatus _VI_FUNC TLUP_getLedCurrentSetpointSource (ViSession instrumentHandle, ViPUInt16 currentSetSource);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_LED_CURR_SET_x */ 


			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_LED_ON_AT_STARTUP_x Source Config LED Switch On At Startup Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are LED instrument startup on state functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setLedSwitchOnAtStartup (ViSession instrumentHandle, ViBoolean ledOnAtStartup);
            TLUP_API ViStatus _VI_FUNC TLUP_getLedSwitchOnAtStartup (ViSession instrumentHandle, ViPBoolean ledOnAtStartup);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_LED_ON_AT_STARTUP_x */


            /*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_LED_OFF_AT_DISCONNECT_x Source Config LED Switch Off At Disconnection Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are LED instrument LED switch off at disconnection functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_setLedSwitchOffAtDisconnect (ViSession instrumentHandle, ViBoolean ledOffAtDisconnect);
			TLUP_API ViStatus _VI_FUNC TLUP_getLedSwitchOffAtDisconnect (ViSession instrumentHandle, ViPBoolean ledOffAtDisconnect);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_LED_OFF_AT_DISCONNECT_x */


			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_USE_NON_THORLABS_LED_x Source Config use Non-Thorlabs LED Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are LED instrument use Non-Thorlabs LED functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_setLedUseNonThorlabsLed (ViSession instrumentHandle, ViBoolean useNonThorlabsLed);
			TLUP_API ViStatus _VI_FUNC TLUP_getLedUseNonThorlabsLed (ViSession instrumentHandle, ViPBoolean useNonThorlabsLed);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_USE_NON_THORLABS_LED_x */

		/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_LED_x */

		
	   /*========================================================================*//**
		\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_x Source Config Functions
		\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
		\brief      This class of functions are TEC instrument specific configuration functions
		@{
		*//*=========================================================================*/
		
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_CURR_LIM_x Source Config Current Limit Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument specific current limit configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setTecCurrLimit (ViSession instrumentHandle, ViReal64 TECCurrentLimit);
            TLUP_API ViStatus _VI_FUNC TLUP_getTecCurrLimit (ViSession instrumentHandle, ViInt16 Attribute, ViPReal64 TECCurrentLimit);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_CURR_LIM_x */

            /*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_VOLT_LIM_x Source Config Voltage Limit Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument specific voltage limit configuration functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_setTecVoltLimit (ViSession instrumentHandle, ViReal64 TECVoltageLimit);
			TLUP_API ViStatus _VI_FUNC TLUP_getTecVoltLimit (ViSession instrumentHandle, ViInt16 Attribute, ViPReal64 TECVoltageLimit);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_VOLT_LIM_x */
			
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_TEMP_SET_x Source Config Temperature Set Value Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument specific temperature setpoint configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setTecTempSetpoint (ViSession instrumentHandle, ViReal64 TECTemperatureSetpoint);
            TLUP_API ViStatus _VI_FUNC TLUP_getTecTempSetpoint (ViSession instrumentHandle, ViInt16 attr, ViPReal64 TECTemperatureSetpoint);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_TEMP_SET_x */
		
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_PID_x Source PID Controller Params Config Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument specific PID controller parameters configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setTecPidParams (ViSession instrumentHandle, ViReal64 pShare, ViReal64 iShare, ViReal64 dShare, ViReal64 period);
            TLUP_API ViStatus _VI_FUNC TLUP_getTecPidParams (ViSession instrumentHandle, ViInt16 attr, ViPReal64 pPShare, ViPReal64 pIShare, ViPReal64 pDShare, ViPReal64 pPeriod);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_PID_x */

            /*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_CRIT_GAIN_PERIOD_x Source Critical Gain and Oscillation Period Params Config Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument specific PID controller parameters configuration functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_setTecCritGainAndOscillationPeriod (ViSession instrumentHandle, ViReal64 pCrit, ViReal64 tCrit);
			TLUP_API ViStatus _VI_FUNC TLUP_getTecCritGainAndOscillationPeriod (ViSession instrumentHandle, ViInt16 attr, ViPReal64 pPCrit, ViPReal64 pTCrit);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_CRIT_GAIN_PERIOD_x */
		
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_PROT_x Source Config Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument specific temperature protection configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setTecTempProtWindow (ViSession instrumentHandle, ViReal64 window);
            TLUP_API ViStatus _VI_FUNC TLUP_getTecTempProtWindow (ViSession instrumentHandle, ViInt16 attr, ViPReal64 window);
            TLUP_API ViStatus _VI_FUNC TLUP_setTecTempProtDelay (ViSession instrumentHandle, ViReal64 delay);
            TLUP_API ViStatus _VI_FUNC TLUP_getTecTempProtDelay (ViSession instrumentHandle, ViInt16 attr, ViPReal64 delay);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_PROT_x */

            /*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_SAFETY_MASK_SET_x Source Config Set Safety Mask Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument set safety mask functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_setTecSafetyMask (ViSession instrumentHandle, ViUInt32 safetyMask);
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_SAFETY_MASK_FLAGS_x Source Config Set Safety Mask Flags
				\ingroup    TLUP_MACROS_x
				@{
				*//*=========================================================================*/
				#define TLUP_TEC_SAFETY_MASK_TRANGE (1) ///< check thermistor temperature range
				#define TLUP_TEC_SAFETY_MASK_ITEC	(2) ///< check tec current being too long on limit value without temperature change
				#define TLUP_TEC_SAFETY_TEC_REV_CON (4) ///< check tec reverse connected detection
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_SAFETY_MASK_SET_FLAGS_x */

			TLUP_API ViStatus _VI_FUNC TLUP_getTecSafetyMask (ViSession instrumentHandle, ViInt16 attr, ViPUInt32 safetyMask);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_SAFETY_MASK_SET_x */

			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_CLEAR_ERROR_x Source Config Set Clear Error Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument set clear error functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_clearTecError (ViSession instrumentHandle);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_SAFETY_CLEAR_ERROR_x */

			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_POL_x TEC Source Set Functions TEC Polarity
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEC_x
			\brief      This class of functions are TEC instrument specific set functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_setTecPolarity (ViSession instr, ViBoolean val);
			TLUP_API ViStatus _VI_FUNC TLUP_getTecPolarity (ViSession instr, ViPBoolean pVal);

				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEC_POL_FLAGS_x TEC Source Set Functions TEC Polarity
				\ingroup    TLUP_MACROS_x
				@{
				*//*=========================================================================*/
				#define TLUP_TEC_POLARITY_NORMAL   (0) ///< Tec polarity normal (default).
				#define TLUP_TEC_POLARITY_REVERSE  (1) ///< Tec polarity reverse.
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_POL_FLAGS_x */

			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_POL_x */

		/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEC_x */

		
	   /*========================================================================*//**
		\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_x Source Config Functions
		\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
		\brief      This class of functions are TEMP instrument specific configuration functions
		@{
		*//*=========================================================================*/
		
			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_SENS_x Source Config Temperature Sensor Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_x
			\brief      This class of functions are TEMP instrument specific temperature sensor configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setTempSensConfig (ViSession instrumentHandle, ViUInt16 temperaturSensorConfiguration);
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_SENS_FLAGS_x Source Config Temperature Sensor Flags
				\ingroup    TLUP_MACROS_x
				@{
				*//*=========================================================================*/
				#define TLUP_TEMP_SENS_8TH  	(0) ///< 8 thermistor channels are available
				#define TLUP_TEMP_SENS_8TC 		(1) ///< 8 thermocouple channels are available
				#define TLUP_TEMP_SENS_4RTD 	(2) ///< 4 resistance temperature device (RTD e.g. Pt100) channels are available
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_SENS_FLAGS_x */
				
            TLUP_API ViStatus _VI_FUNC TLUP_getTempSensConfig (ViSession instrumentHandle, ViPUInt16 temperaturSensorConfiguration);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_SENS_x */
		

            /*========================================================================*//**
            \defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_SENS_CONVERT_x Source Config Thermistor Sensor Parameter Convertion Functions
            \ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_SENS_x
            \brief      This class of functions are TEMP instrument specific temperature sensor parameter conversion functions
            @{
            *//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_getSteinhartHartParameterFromExponentialParameterConvertion (ViSession instr, ViReal64 t0, ViReal64 r0, ViReal64 beta,
                                                                                                         ViPReal64 steinhartHartParamA, ViPReal64 steinhartHartParamB, ViPReal64 steinhartHartParamC,
																	                                     ViPReal64 steinhartHartParamD, ViPReal64 steinhartHartParamE, ViPReal64 steinhartHartParamF);
            /**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_CONVERT_x */

            /*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_SENS_RANGES_x Source Config Thermistor Sensor Temperature Ranges Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_SENS_x
			\brief      This class of functions are TEMP instrument specific temperature sensor temperature ranges functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_getTemperatureRangesFromSteinhartHartParameters (ViSession instr,
																							 ViReal64 steinhartHartParamA, ViReal64 steinhartHartParamB, ViReal64 steinhartHartParamC,
																	                         ViReal64 steinhartHartParamD, ViReal64 steinhartHartParamE, ViReal64 steinhartHartParamF,
																	                         ViReal64 tempRangesMin[], ViReal64 tempRangesMax[]);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_RANGES_x */

            /*========================================================================*//**
            \defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_SENS_x Source Config Thermistor Sensor Functions
            \ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_x
            \brief      This class of functions are TEMP instrument specific temperature sensor configuration functions
            @{
            *//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setThermSensConfig (ViSession instrumentHandle, ViUInt16 numberOfHardwareChannel, ViUInt16 temperatureRange,
                                                                ViReal64 steinhartHartParamA, ViReal64 steinhartHartParamB, ViReal64 steinhartHartParamC,
                                                                ViReal64 steinhartHartParamD, ViReal64 steinhartHartParamE, ViReal64 steinhartHartParamF);
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_SENS_FLAGS_x Source Config Thermistor Sensor Flags
				\ingroup    TLUP_MACROS_x
				@{
				*//*=========================================================================*/
				#define TLUP_THERM_TEMP_RANGE_250NA     (0) ///< thermistor excitation current 250 nA
				#define TLUP_THERM_TEMP_RANGE_500NA     (1) ///< thermistor excitation current 500 nA
				#define TLUP_THERM_TEMP_RANGE_1UA       (2) ///< thermistor excitation current   1 µA
				#define TLUP_THERM_TEMP_RANGE_5UA       (3) ///< thermistor excitation current   5 µA
				#define TLUP_THERM_TEMP_RANGE_10UA      (4) ///< thermistor excitation current  10 µA
				#define TLUP_THERM_TEMP_RANGE_25UA      (5) ///< thermistor excitation current  25 µA
				#define TLUP_THERM_TEMP_RANGE_50UA      (6) ///< thermistor excitation current  50 µA
				#define TLUP_THERM_TEMP_RANGE_100UA     (7) ///< thermistor excitation current 100 µA
                #define TLUP_THERM_TEMP_RANGE_UNKNOWN   (8) ///< thermistor excitation current is unknown
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_SENS_FLAGS_x */

            TLUP_API ViStatus _VI_FUNC TLUP_getThermSensConfig (ViSession instrumentHandle, ViUInt16 numberOfHardwareChannel,ViPUInt16 pTemperatureRange,
														ViPReal64 steinhartHartParamA, ViPReal64 steinhartHartParamB, ViPReal64 steinhartHartParamC,
														ViPReal64 steinhartHartParamD, ViPReal64 steinhartHartParamE, ViPReal64 steinhartHartParamF);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_THERM_SENS_x */


			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_RTD_SENS_x Source Config RTD Sensor Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are TEMP instrument specific temperature sensor configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setRtdSensConfig (ViSession instrumentHandle, ViUInt16 numberOfHardwareChannel, ViUInt16 rtdType, ViUInt16 curveType);
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_RTD_SENS_FLAGS_x Source Config RTD Sensor Flags
				\ingroup    TLUP_MACROS_x
				@{
				*//*=========================================================================*/
				#define TLUP_RTD_TYPE_PT100  	(1) ///< RTD type PT100
				#define TLUP_RTD_TYPE_PT200  	(2) ///< RTD type PT200
				#define TLUP_RTD_TYPE_PT500  	(3) ///< RTD type PT500
				#define TLUP_RTD_TYPE_PT1000  	(4) ///< RTD type PT1000

				#define TLUP_RTD_CURVE_EUROPE  	(1) ///< RTD curve type Europa
				#define TLUP_RTD_CURVE_AMERICA 	(2) ///< RTD curve type America
				#define TLUP_RTD_CURVE_JAPAN  	(3) ///< RTD curve type Japan
				#define TLUP_RTD_CURVE_ITS90  	(4) ///< RTD curve type ITS90
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_RTD_SENS_FLAGS_x */

            TLUP_API ViStatus _VI_FUNC TLUP_getRtdSensConfig (ViSession instrumentHandle, ViUInt16 numberOfHardwareChannel, ViPUInt16 rtdType, ViPUInt16 curveType);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_RTD_SENS_x */


			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_TC_SENS_x Source Config TC Sensor Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_x
			\brief      This class of functions are TEMP instrument specific temperature sensor configuration functions
			@{
			*//*=========================================================================*/
            TLUP_API ViStatus _VI_FUNC TLUP_setTcSensConfig (ViSession instrumentHandle, ViUInt16 numberOfHardwareChannel, ViUInt16 tcType);
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_TC_SENS_FLAGS_x Source Config TC Sensor Flags
				\ingroup    TLUP_MACROS_x
				@{
				*//*=========================================================================*/
				#define TLUP_TC_TYPE_J  	(1) ///< TC type J
				#define TLUP_TC_TYPE_K  	(2) ///< TC type K
				#define TLUP_TC_TYPE_E  	(3) ///< TC type E
				#define TLUP_TC_TYPE_N  	(4) ///< TC type N
				#define TLUP_TC_TYPE_R  	(5) ///< TC type R
				#define TLUP_TC_TYPE_S  	(6) ///< TC type S
				#define TLUP_TC_TYPE_T  	(7) ///< TC type T
				#define TLUP_TC_TYPE_B  	(8) ///< TC type B
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_TC_SENS_FLAGS_x */

            TLUP_API ViStatus _VI_FUNC TLUP_getTcSensConfig (ViSession instrumentHandle, ViUInt16 numberOfHardwareChannel, ViPUInt16 tcType);
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_TC_SENS_x */


            /*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_CHAN_LIST_x Source Config Temperature Channel List Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_x
			\brief      This class of functions are TEMP instrument specific temperature channel list configuration functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_setMeasChanList (ViSession instrumentHandle, ViUInt8 measChan[]);
			TLUP_API ViStatus _VI_FUNC TLUP_getMeasChanList (ViSession instrumentHandle, ViUInt8 measChan[]);
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_CHAN_LIST_FLAGS_x Source Config Temperature max. number of measurement channels Flags
				\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_x
				@{
				*//*=========================================================================*/
				#define TLUP_TEMP_CHAN_LIST_MAX_NUM_CHAN	(8)	///< maximum number of temperature measurement channels
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_CHAN_LIST_FLAGS_x */
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_CHAN_LIST_x */


			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_OFFS_LIST_x Source Config Temperature Offset List Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_x
			\brief      This class of functions are TEMP instrument specific temperature offset list configuration functions
			@{
			*//*=========================================================================*/
			TLUP_API ViStatus _VI_FUNC TLUP_calcTempOffsets (ViSession instr, ViReal64 tempSetpoint, ViReal64 tempMeas[], ViReal64 tempOffs[]);

			TLUP_API ViStatus _VI_FUNC TLUP_setTempOffsets (ViSession instrumentHandle, ViReal64 temperatureOffsets[]);
			TLUP_API ViStatus _VI_FUNC TLUP_getTempOffsets (ViSession instrumentHandle, ViReal64 temperatureOffsets[]);
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_OFFS_LIST_FLAGS_x Source Config Temperature max. number of measurement channels Flags
				\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_x
				@{
				*//*=========================================================================*/
				#define TLUP_TEMP_OFFS_LIST_MAX_NUM_CHAN	(8)	///< maximum number of temperature offset channels
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_OFFS_LIST_FLAGS_x */
			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_OFFS_LIST_x */


			/*========================================================================*//**
			\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_x Source Config Temperature Acquisition Functions
			\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_x
			\brief      This class of functions are TEMP instrument specific temperature acquisition configuration functions
			@{
			*//*=========================================================================*/
				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NUM_DATA_SETS_x Source Config Temperature Channel List Functions
				\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_x
				\brief      This class of functions are TEMP instrument specific temperature acquisition data sets functions
				@{
				*//*=========================================================================*/
                TLUP_API ViStatus _VI_FUNC TLUP_getNumDataSets (ViSession instrumentHandle, ViPUInt16 numDataSets);
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NUM_DATA_SETS_x */

				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_DATA_SET_DELETE_x Source Config Temperature Data delete Data Set Functions
				\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_DATA_SET_x
				\brief      This class of functions are TEMP instrument specific temperature acquisition delete data set functions
				@{
				*//*=========================================================================*/
                TLUP_API ViStatus _VI_FUNC TLUP_deleteDataSet (ViSession instrumentHandle, ViUInt16 dataSetDelete);
					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_DATA_SET_DELETE_FLAGS_x Source Config Temperature delete Data Set Flags
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_DATA_SET_x
					@{
					*//*=========================================================================*/
					#define TLUP_TEMP_DATA_DELETE_NEW	 (0)	///< delete newest data set in directory
					#define TLUP_TEMP_DATA_DELETE_ALL	 (1)	///< delete all data sets in directory
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_DATA_SET_DELETE_FLAGS_x */
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_DATA_SET_DELETE_x */

				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x Source Config Temperature current Data Set Functions
				\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_x
				\brief      This class of functions are TEMP instrument specific temperature acquisition current data set functions
				@{
				*//*=========================================================================*/
					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NUM_x Source Config Temperature current Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition current data set functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_selectCurrDataSet (ViSession instrumentHandle, ViUInt16 datasetNo);
                    TLUP_API ViStatus _VI_FUNC TLUP_selectedCurrDataSet (ViSession instrumentHandle, ViPUInt16 pDataSetNo);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NUM_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_RUN_STATE_x Source Config Temperature Run State of current Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition data set run state functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getRunStateCurrDataSet (ViSession instrumentHandle, ViPBoolean runState);
                    	/*========================================================================*//**
						\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_RUN_STATE_FLAGS_x Source Config Temperature Run State of current Data Set Flags
						\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
						@{
						*//*=========================================================================*/
						#define TLUP_TEMP_DATA_ACQU_NOT_RUNNING	(0)	///< data acquisition is not running
						#define TLUP_TEMP_DATA_ACQU_RUNNING	 	(1)	///< data acquisition is currently running
						/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_RUN_STATE_FLAGS_x */
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_RUN_STATE_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NAME_x Source Config Temperature Name of current Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition current data set name functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getNameCurrDataSet (ViSession instrumentHandle, ViChar _VI_FAR name[]);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NAME_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_START_TIME_x Source Config Temperature Start Time of current Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition data set start time functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getStartTimeCurrDataSet (ViSession instrumentHandle, ViPUInt16 year, ViPUInt16 month, ViPUInt16 day, ViPUInt16 hour, ViPUInt16 minute, ViPUInt16 second);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_START_TIME_x */


					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NUM_POINTS_x Source Config Temperature Number of Points in current Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition current data set number of points functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getColumnCountCurrDataSet (ViSession instrumentHandle, ViPUInt32 pColumnCount);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NUM_POINTS_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NUM_SEC_POINT_TO_POINT_x Source Config Temperature Number Seconds from Point to Point in current Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition current data set number of seconds from point to point functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getTimeDistCurrDataSet (ViSession instrumentHandle, ViPUInt32 pMeasurementInterval);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NUM_SEC_POINT_TO_POINT_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NUM_VAL_PER_POINT__x Source Config Temperature Number of Values per Point in current Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition current data set number of values per point functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getRowCountCurrDataSet (ViSession instrumentHandle, ViPUInt16 pMeasuredChannels);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_NUM_VAL_PER_POINT__x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_CONFIG_x Source Config Temperature Channel Configuration Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition data set configuration functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getSensConfigCurrDataSet (ViSession instrumentHandle, ViPUInt16 temperaturSensorConfiguration);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_CONFIG_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_LIST_MEAS_CHAN_x Source Config Temperature List of Measurement Channels of current Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition data set list of measurement channels functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getMeasChanListCurrDataSet (ViSession instrumentHandle, ViUInt8 measChan[]);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_LIST_MEAS_CHAN_x */


					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_GET_SINGLE_VAL_x Source Config Temperature Get Single Measurement Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition data set get single measurement functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getSingleValCurrDataSet (ViSession instrumentHandle, ViUInt32 columnNumber, ViUInt8 channelNumber, ViPReal64 measurementValue);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_GET_SINGLE_VAL_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_GET_ALL_VAL_x Source Config Temperature Get All Measurements Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition data set get all measurements functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_getAllValCurrDataSet (ViSession instrumentHandle, ViUInt32 columnNumber, ViReal64 measurementValues[]);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_GET_ALL_VAL_x */
				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_CURR_DATA_SET_x */

				/*========================================================================*//**
				\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_x Source Config Temperature next Data Set Functions
				\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_x
				\brief      This class of functions are TEMP instrument specific temperature acquisition next data set functions
				@{
				*//*=========================================================================*/

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_NAME_x Source Config Temperature Name of next Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition next data set name functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_setNameNextDataSet (ViSession instrumentHandle, ViChar _VI_FAR name[]);
                    TLUP_API ViStatus _VI_FUNC TLUP_getNameNextDataSet (ViSession instrumentHandle, ViChar _VI_FAR name[]);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_NAME_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_MEAS_CHAN_x Source Config Temperature Measurement Channels of next Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition next data set measurement channels functions
					@{
					*//*=========================================================================*/
//                    TLUP_API ViStatus _VI_FUNC TLUP_setMeasChanListNextDataSet (ViSession instrumentHandle, ViChar _VI_FAR measChan[]); // only TLUP_setMeasChanList() used
//                    TLUP_API ViStatus _VI_FUNC TLUP_getMeasChanListNextDataSet (ViSession instrumentHandle, ViChar _VI_FAR measChan[]); // only TLUP_getMeasChanList() used
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_MEAS_CHAN_x */

                    /*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_SENS_CONF_x Sensor Config Temperature Measurement Channels of next Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition next data set sensor configuration functions
					@{
					*//*=========================================================================*/
//                    TLUP_API ViStatus _VI_FUNC TLUP_setSensConfNextDataSet (ViSession instrumentHandle, ViChar _VI_FAR sensConf[]); // only TLUP_setTempSensConfig() used
//					TLUP_API ViStatus _VI_FUNC TLUP_getSensConfNextDataSet (ViSession instrumentHandle, ViChar _VI_FAR sensConf[]);   // only TLUP_setTempSensConfig() used
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_SENF_CONF_x */

					/*========================================================================*//**
					\defgroup   TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_TIME_DIST_x Source Config Temperature Time Distance of next Data Set Functions
					\ingroup    TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_x
					\brief      This class of functions are TEMP instrument specific temperature acquisition next data set time distance functions
					@{
					*//*=========================================================================*/
                    TLUP_API ViStatus _VI_FUNC TLUP_setTimeDistNextDataSet (ViSession instrumentHandle, ViUInt32 timeDist);
                    TLUP_API ViStatus _VI_FUNC TLUP_getTimeDistNextDataSet (ViSession instrumentHandle, ViInt16 attr, ViPUInt32 timeDist);
					/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_TIME_DIST_x */

				/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_NEXT_DATA_SET_x */

			/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_ACQU_x */

		/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_TEMP_x */

	/**@}*/  /* TLUP_METHODS_SOURCE_CONFIG_x */

/**@}*/  /* TLUP_METHODS_SOURCE_x */ 



/*========================================================================*//**
\defgroup   TLUP_METHODS_UTILITY_x Utility Functions
\ingroup    TLUP_METHODS_x
\brief      This class of functions provides utility and lower level functions to communicate with the instrument.
@{
*//*=========================================================================*/ 
TLUP_API ViStatus _VI_FUNC TLUP_errorMessage (ViSession instrumentHandle, ViStatus errorCode, ViChar _VI_FAR errorMessage[]);
TLUP_API ViStatus _VI_FUNC TLUP_errorQuery (ViSession instrumentHandle, ViPStatus errorCode, ViChar _VI_FAR errorMessage[]);
TLUP_API ViStatus _VI_FUNC TLUP_reset (ViSession instrumentHandle);
TLUP_API ViStatus _VI_FUNC TLUP_selfTest (ViSession instrumentHandle, ViPInt16 selfTestResult, ViChar _VI_FAR selfTestMessage[]);
TLUP_API ViStatus _VI_FUNC TLUP_revisionQuery (ViSession instrumentHandle, ViChar _VI_FAR instrumentDriverRevision[], ViChar _VI_FAR firmwareRevision[]);
TLUP_API ViStatus _VI_FUNC TLUP_identificationQuery (ViSession instrumentHandle, ViChar _VI_FAR manufacturerName[], ViChar _VI_FAR deviceName[], ViChar _VI_FAR serialNumber[], ViChar _VI_FAR firmwareRevision[]);
/*
// the following functionallity is always realized in TLUP_identificationQuery()
TLUP_API ViStatus _VI_FUNC TLUP_getManufacturerName (ViSession instrumentHandle, ViChar _VI_FAR manufacturerName[]);
TLUP_API ViStatus _VI_FUNC TLUP_getDeviceName (ViSession instrumentHandle, ViChar _VI_FAR deviceName[]);
TLUP_API ViStatus _VI_FUNC TLUP_getSerialNumber (ViSession instrumentHandle,  ViChar _VI_FAR serialNumber[]);
TLUP_API ViStatus _VI_FUNC TLUP_getRevisionNumber (ViSession instrumentHandle, ViChar _VI_FAR firmwareRevision[]);
*/
TLUP_API ViStatus _VI_FUNC TLUP_getBuildDateAndTime (ViSession instr, ViChar _VI_FAR buildDateAndTime[]);
TLUP_API ViStatus _VI_FUNC TLUP_getCalibrationMsg (ViSession instrumentHandle, ViChar _VI_FAR message[]);
/**@}*/  /* TLUP_METHODS_UTILITY_x */

/**@}*/  /* TLUP_METHODS_x */	 
	
#if defined(__cplusplus) || defined(__cplusplus__)
}
#endif

#endif  /* ndef _TLUP_DRIVER_HEADER_ */

/*- The End -----------------------------------------------------------------*/


