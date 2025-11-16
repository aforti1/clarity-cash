import { Box, Button, Text, VStack } from '@chakra-ui/react'

interface ScoreModalProps {
    isOpen: boolean
    onClose: () => void
    score: number
    reasons: string
    description: string
}

function ScoreModal({ isOpen, onClose, score, reasons, description }: ScoreModalProps) {
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
                bg="gray.900"
                w="90%"
                maxW="800px"
                maxH="90vh"
                zIndex={1000}
                borderRadius="md"
                boxShadow="xl"
                border="1px solid"
                borderColor="gray.800"
                overflow="auto"
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
                    color="gray.100"
                    _hover={{ bg: "gray.800" }}
                >
                    X
                </Button>

                {/* Content */}
                <VStack gap={8} p={12} pt={16} alignItems="stretch">
                    {/* Score Slider Section */}
                    <VStack alignItems="stretch" gap={4}>
                        <Text fontSize="4xl" fontWeight="bold" color="gray.100">
                            Score
                        </Text>

                        <Box position="relative" w="full">
                            {/* Slider Line */}
                            <Box
                                h="2px"
                                bg="gray.700"
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
                                    bg="blue.500"
                                    borderRadius="full"
                                />
                            </Box>

                            {/* 0 and 100 labels */}
                            <Box display="flex" justifyContent="space-between" mt={2}>
                                <Text fontSize="3xl" fontWeight="bold" color="gray.100">0</Text>
                                <Text fontSize="3xl" fontWeight="bold" color="gray.100">100</Text>
                            </Box>
                        </Box>
                    </VStack>

                    {/* Divider */}
                    <Box h="1px" bg="gray.800" />

                    {/* Description Section */}
                    <VStack alignItems="stretch" gap={4}>
                        <Text fontSize="4xl" fontWeight="bold" color="gray.100">
                            Description
                        </Text>

                        <Box
                            bg="gray.800"
                            p={6}
                            minH="150px"
                            borderRadius="md"
                            border="1px solid"
                            borderColor="gray.700"
                        >
                            <Text fontSize="lg" color="gray.100" whiteSpace="pre-wrap">
                                {description || 'No description available.'}
                            </Text>
                        </Box>
                    </VStack>

                    {/* Divider */}
                    <Box h="1px" bg="gray.800" />

                    {/* Reasons Section */}
                    <VStack alignItems="stretch" gap={4}>
                        <Text fontSize="4xl" fontWeight="bold" color="gray.100">
                            Reasons
                        </Text>

                        <Box
                            bg="gray.800"
                            p={6}
                            minH="300px"
                            borderRadius="md"
                            border="1px solid"
                            borderColor="gray.700"
                        >
                            <Text fontSize="lg" color="gray.100" whiteSpace="pre-wrap">
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