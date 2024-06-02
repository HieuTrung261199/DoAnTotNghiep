################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (10.3-2021.10)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Custom/Src/stm32f4xx_driver_gpio.c \
../Custom/Src/stm32f4xx_i2c_driver.c \
../Custom/Src/stm32f4xx_rcc_driver.c \
../Custom/Src/stm32f4xx_spi_driver.c 

OBJS += \
./Custom/Src/stm32f4xx_driver_gpio.o \
./Custom/Src/stm32f4xx_i2c_driver.o \
./Custom/Src/stm32f4xx_rcc_driver.o \
./Custom/Src/stm32f4xx_spi_driver.o 

C_DEPS += \
./Custom/Src/stm32f4xx_driver_gpio.d \
./Custom/Src/stm32f4xx_i2c_driver.d \
./Custom/Src/stm32f4xx_rcc_driver.d \
./Custom/Src/stm32f4xx_spi_driver.d 


# Each subdirectory must supply rules for building sources it contributes
Custom/Src/%.o Custom/Src/%.su: ../Custom/Src/%.c Custom/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F411xE -c -I../Core/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../Drivers/CMSIS/Include -I"D:/STM32/Test/Custom/Inc" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Custom-2f-Src

clean-Custom-2f-Src:
	-$(RM) ./Custom/Src/stm32f4xx_driver_gpio.d ./Custom/Src/stm32f4xx_driver_gpio.o ./Custom/Src/stm32f4xx_driver_gpio.su ./Custom/Src/stm32f4xx_i2c_driver.d ./Custom/Src/stm32f4xx_i2c_driver.o ./Custom/Src/stm32f4xx_i2c_driver.su ./Custom/Src/stm32f4xx_rcc_driver.d ./Custom/Src/stm32f4xx_rcc_driver.o ./Custom/Src/stm32f4xx_rcc_driver.su ./Custom/Src/stm32f4xx_spi_driver.d ./Custom/Src/stm32f4xx_spi_driver.o ./Custom/Src/stm32f4xx_spi_driver.su

.PHONY: clean-Custom-2f-Src

