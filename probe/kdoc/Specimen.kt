package probe.kdoc

/**
 * Normalizes a label with [String.trim] and preserves intentional whitespace in this example so the formatter must reflow this paragraph without changing its words.
 *
 * - Trim leading whitespace.
 * - Trim trailing whitespace.
 *
 * ```kotlin
 * val source = "  example  "
 * val label = normalizeLabel(source)
 * ```
 *
 * @param source the untrimmed label
 * @return the trimmed label
 */
fun normalizeLabel(source: String): String = source.trim()
