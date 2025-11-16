/* Subtitle for the landing page */
import { Text } from "@chakra-ui/react";
import { keyframes } from '@emotion/react';

// Define the fade animation
const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

export function Subtitle() {
  return (
      <Text 
        color="gray.400"
        textAlign="center"
        fontSize="2xl"
        maxW="900px"
        animation={`${fadeIn} 2.5s ease-out 1s both`}
      >
        Smarter spending decisions powered by real-time purchase analysis.
      </Text>
  );
}