plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.paparazzi)
}

android {
    namespace = "bench.paparazzi"
    compileSdk = 37
    defaultConfig { minSdk = 24 }
}

// The shared fixtures, added through the variant API: AGP 9's typed `sourceSets` accessor in the
// Kotlin DSL fails with a ClassCastException on a library module.
androidComponents {
    onVariants { variant ->
        variant.sources.kotlin?.addStaticSourceDirectory("../fixtures/src")
    }
}

dependencies {
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.material3)
    testImplementation(libs.junit4)
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
}
