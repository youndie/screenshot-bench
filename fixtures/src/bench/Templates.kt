package bench

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.Typography
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

// Five screen shapes that a real app is made of: a list, a form, a grid of cards, a profile with
// controls, a settings page. A fixture is one of them with a seed, so N fixtures are N different
// images of comparable weight, and no tool gets a cheaper picture than another.
//
// Only foundation and material3 — no icons artifact, no resources — so the same file compiles
// against Jetpack Compose (Paparazzi, Roborazzi/Robolectric) and Compose Multiplatform (viddik,
// Roborazzi/desktop) unchanged.

private val BenchColors = lightColorScheme(
    primary = Color(0xFF3D5AFE),
    secondary = Color(0xFF00897B),
    tertiary = Color(0xFFF4511E),
    background = Color(0xFFFAFAFA),
    surface = Color(0xFFFFFFFF),
)

private val Swatches = listOf(
    Color(0xFF3D5AFE), Color(0xFF00897B), Color(0xFFF4511E), Color(0xFF8E24AA),
    Color(0xFFFDD835), Color(0xFF43A047), Color(0xFF6D4C41), Color(0xFF1E88E5),
)

private val Words = listOf(
    "Invoice", "Transfer", "Groceries", "Rent", "Salary", "Coffee", "Taxi", "Books",
    "Cinema", "Gym", "Pharmacy", "Flowers", "Hardware", "Parking", "Travel", "Gifts",
)

/**
 * Set by -PbenchPerturb on the test JVM, to check that a verify can fail at all: `word` replaces the
 * first letter of every screen's heading with X, `dot` appends a full stop to it. A tool whose verify
 * passes after that is comparing nothing, or comparing with a tolerance wider than the change.
 */
private val Perturb: String = System.getProperty("bench.perturb").orEmpty()

private fun heading(text: String) = when (Perturb) {
    "word" -> "X" + text.drop(1)
    "dot" -> "$text."
    else -> text
}

private fun word(seed: Int, i: Int) = Words[(seed * 7 + i * 3) % Words.size]
private fun swatch(seed: Int, i: Int) = Swatches[(seed + i) % Swatches.size]

/** A fixed theme, so a golden depends on the fixture and not on the host. [typography] is the one
 * knob a harness may turn: a tool that bundles a font says so there. */
@Composable
fun BenchTheme(typography: Typography = Typography(), content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = BenchColors, typography = typography) {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            content()
        }
    }
}

@Composable
fun ListScreen(seed: Int) {
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text(heading("Payments #$seed"), style = MaterialTheme.typography.headlineSmall)
        Spacer(Modifier.height(8.dp))
        repeat(9) { i ->
            Row(
                Modifier.fillMaxWidth().padding(vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(Modifier.size(40.dp).clip(CircleShape).background(swatch(seed, i)))
                Column(Modifier.weight(1f).padding(horizontal = 12.dp)) {
                    Text(word(seed, i), style = MaterialTheme.typography.titleMedium)
                    Text("${(seed * 13 + i * 17) % 28 + 1} Sep", style = MaterialTheme.typography.bodySmall)
                }
                Text("−${(seed * 31 + i * 97) % 900 + 10}.00", fontWeight = FontWeight.SemiBold)
            }
            if (i < 8) HorizontalDivider()
        }
    }
}

@Composable
fun FormScreen(seed: Int) {
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(heading("Sign up, step ${seed % 4 + 1}"), style = MaterialTheme.typography.headlineSmall)
        OutlinedTextField(value = "user$seed@example.com", onValueChange = {}, label = { Text("Email") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = word(seed, 1), onValueChange = {}, label = { Text("Display name") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = "", onValueChange = {}, label = { Text("Referral code") }, modifier = Modifier.fillMaxWidth())
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(checked = seed % 2 == 0, onCheckedChange = {})
            Text("I accept the terms of service")
        }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(checked = seed % 3 == 0, onCheckedChange = {})
            Text("Send me the newsletter")
        }
        Spacer(Modifier.weight(1f))
        Button(onClick = {}, modifier = Modifier.fillMaxWidth()) { Text("Continue") }
        OutlinedButton(onClick = {}, modifier = Modifier.fillMaxWidth()) { Text("Back") }
    }
}

@Composable
fun CardGrid(seed: Int) {
    Column(Modifier.fillMaxSize().padding(12.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(heading("Collections"), style = MaterialTheme.typography.headlineSmall, modifier = Modifier.padding(4.dp))
        repeat(3) { row ->
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                repeat(2) { col ->
                    val i = row * 2 + col
                    Card(Modifier.weight(1f).height(160.dp)) {
                        Box(Modifier.fillMaxWidth().height(96.dp).background(swatch(seed, i)))
                        Column(Modifier.padding(8.dp)) {
                            Text(word(seed, i), style = MaterialTheme.typography.titleSmall)
                            Text("${(seed + i) % 40 + 2} items", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ProfileScreen(seed: Int) {
    Column(Modifier.fillMaxSize().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            Modifier.size(96.dp).clip(CircleShape).background(swatch(seed, 0))
                .border(4.dp, MaterialTheme.colorScheme.primary, CircleShape),
            contentAlignment = Alignment.Center,
        ) {
            Text(word(seed, 0).take(2).uppercase(), color = Color.White, style = MaterialTheme.typography.headlineMedium)
        }
        Spacer(Modifier.height(12.dp))
        Text(heading("${word(seed, 2)} ${word(seed, 5)}"), style = MaterialTheme.typography.titleLarge)
        Text("Member since 20${10 + seed % 16}", style = MaterialTheme.typography.bodyMedium)
        Spacer(Modifier.height(16.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            repeat(3) { i -> AssistChip(onClick = {}, label = { Text(word(seed, i + 3)) }) }
        }
        Spacer(Modifier.height(16.dp))
        Text("Monthly limit", modifier = Modifier.fillMaxWidth())
        Slider(value = (seed % 10) / 10f, onValueChange = {})
        Text("Storage used", modifier = Modifier.fillMaxWidth())
        LinearProgressIndicator(progress = { (seed % 7 + 1) / 8f }, modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp))
        Spacer(Modifier.weight(1f))
        Box(
            Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(MaterialTheme.colorScheme.secondary).padding(16.dp),
        ) {
            Text("Upgrade to Pro — ${seed % 5 + 1} months free", color = Color.White)
        }
    }
}

@Composable
fun SettingsScreen(seed: Int) {
    Column(Modifier.fillMaxSize().padding(vertical = 16.dp)) {
        Text(heading("Settings"), style = MaterialTheme.typography.headlineSmall, modifier = Modifier.padding(horizontal = 16.dp))
        repeat(8) { i ->
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(Modifier.size(24.dp).clip(RoundedCornerShape(6.dp)).background(swatch(seed, i)))
                Spacer(Modifier.width(16.dp))
                Column(Modifier.weight(1f)) {
                    Text("${word(seed, i)} notifications")
                    Text("Delivered ${if ((seed + i) % 2 == 0) "instantly" else "as a daily digest"}", style = MaterialTheme.typography.bodySmall)
                }
                Switch(checked = (seed + i) % 3 != 0, onCheckedChange = {})
            }
        }
    }
}
