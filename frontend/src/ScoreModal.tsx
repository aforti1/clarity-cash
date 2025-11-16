import { Box, Button, Text, VStack } from '@chakra-ui/react'

interface ScoreModalProps {
    isOpen: boolean
    onClose: () => void
    score: number
    reasons: string
}

function ScoreModal({ isOpen, onClose, score, reasons }: ScoreModalProps) {
    if (!isOpen) return null

    return (
        <>
            {/* Overlay */}
            <Box
                position="fixed"
                top={0}
                left={0}
                right={0}
                bottom={0}
                bg="blackAlpha.600"
                zIndex={999}
                onClick={onClose}
            />

            {/* Modal */}
            <Box
                position="fixed"
                top="50%"
                left="50%"
                transform="translate(-50%, -50%)"
                bg="white"
                w="90%"
                maxW="800px"
                maxH="90vh"
                zIndex={1000}
                borderRadius="md"
                boxShadow="xl"
                overflow="hidden"
            >
                {/* Close Button */}
                <Button
                    position="absolute"
                    top={4}
                    left={4}
                    variant="ghost"
                    onClick={onClose}
                    fontSize="2xl"
                    fontWeight="bold"
                    p={2}
                >
                    X
                </Button>

                {/* Content */}
                <VStack gap={8} p={12} pt={16} alignItems="stretch">
                    {/* Score Slider Section */}
                    <VStack alignItems="stretch" gap={4}>
                        <Text fontSize="4xl" fontWeight="bold" color="gray.700">
                            Score
                        </Text>

                        <Box position="relative" w="full">
                            {/* Slider Line */}
                            <Box
                                h="2px"
                                bg="gray.800"
                                position="relative"
                                my={4}
                            >
                                {/* Score Circle */}
                                <Box
                                    position="absolute"
                                    left={`${score}%`}
                                    top="50%"
                                    transform="translate(-50%, -50%)"
                                    w="20px"
                                    h="20px"
                                    bg="gray.400"
                                    borderRadius="full"
                                />
                            </Box>

                            {/* 0 and 100 labels */}
                            {/* 0 and 100 labels */}
                            <Box display="flex" justifyContent="space-between" mt={2}>
                                <Text fontSize="3xl" fontWeight="bold" color="black">0</Text>
                                <Text fontSize="3xl" fontWeight="bold" color="black">100</Text>
                            </Box>
                        </Box>
                    </VStack>

                    {/* Divider */}
                    <Box h="1px" bg="gray.300" />

                    {/* Reasons Section */}
                    <VStack alignItems="stretch" gap={4}>
                        <Text fontSize="4xl" fontWeight="bold" color="gray.700">
                            Reasons
                        </Text>

                        <Box
                            bg="gray.200"
                            p={6}
                            minH="300px"
                            borderRadius="md"
                        >
                            <Text fontSize="lg" color="black" whiteSpace="pre-wrap">
                                {reasons}
                            </Text>
                        </Box>
                    </VStack>
                </VStack>
            </Box>
        </>
    )
}

export default ScoreModal