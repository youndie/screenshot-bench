plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose.multiplatform)
    alias(libs.plugins.roborazzi)
}

kotlin {
    sourceSets.named("main") { kotlin.srcDir("../fixtures/src") }
}

dependencies {
    implementation(compose.desktop.currentOs)
    implementation(libs.cmp.material3)
    testImplementation(libs.roborazzi.compose.desktop)
    testImplementation(compose.desktop.uiTestJUnit4)
    testImplementation(libs.junit4)
    // Only for -PbenchFont=viddik: the same bundled, metric-normalised Roboto viddik's fixtures use,
    // so the cross-OS comparison can separate what the font does from what the capture engine does.
    testImplementation(libs.viddik.testing.core)
}

// A benchmark run must execute, not come back from an up-to-date check: every run passes a fresh
// -PbenchRun, which is an input of every Test task. -PbenchForks is the one tuning knob, the same
// for all four tools; -PbenchPerturb changes the pictures to prove a verify can fail.
tasks.withType<Test>().configureEach {
    inputs.property("benchRun", providers.gradleProperty("benchRun").orElse("0"))
    providers.gradleProperty("benchForks").orNull?.let { maxParallelForks = it.toInt() }
    providers.gradleProperty("benchPerturb").orNull?.let { systemProperty("bench.perturb", it) }
    // Gradle's own default test heap is 512 MB for every tool; -PbenchHeap raises it for all alike.
    providers.gradleProperty("benchHeap").orNull?.let { maxHeapSize = it }
    providers.gradleProperty("benchFont").orNull?.let { systemProperty("bench.font", it) }
}
