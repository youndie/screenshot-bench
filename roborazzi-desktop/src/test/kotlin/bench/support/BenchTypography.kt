package bench

import androidx.compose.material3.Typography
import io.github.youndie.viddik.core.viddikTypography

/**
 * The platform default font unless -PbenchFont=viddik, which swaps in viddik's bundled Roboto with
 * normalised vertical metrics and fixed rasterisation settings. Roborazzi's own capture path is
 * unchanged either way.
 */
fun benchTypography(): Typography =
    if (System.getProperty("bench.font") == "viddik") viddikTypography() else Typography()
