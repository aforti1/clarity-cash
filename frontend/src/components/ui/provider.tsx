"use client"

import { ChakraProvider, defaultSystem, type SystemContext } from "@chakra-ui/react"
import {
  ColorModeProvider,
  type ColorModeProviderProps,
} from "./color-mode"

interface ProviderProps extends ColorModeProviderProps {
  value?: SystemContext
}

export function Provider({ value = defaultSystem, ...props }: ProviderProps) {
  return (
    <ChakraProvider value={value}>
      <ColorModeProvider {...props} />
    </ChakraProvider>
  )
}
