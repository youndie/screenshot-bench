plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose.multiplatform)
    alias(libs.plugins.ksp)
    alias(libs.plugins.viddik)
}

kotlin {
    sourceSets.named("main") { kotlin.srcDir("../fixtures/src") }
}

dependencies {
    implementation(compose.desktop.currentOs)
    implementation(libs.cmp.material3)
}

viddik {
    // Under build/, like the other three: the goldens are an output of the run, not a fixture.
    snapshotsDir = "build/goldens"
    // viddik sets the Test task's maxParallelForks from `shards` itself (two by default), so the
    // shared -PbenchForks knob has to go through here to mean the same thing as for the others.
    providers.gradleProperty("benchForks").orNull?.let { shards = it.toInt() }
    // -PbenchStrict: no share and no per-channel allowance, to see what the default tolerance is
    // buying. The engine's 16-pixel floor stays; it has no switch.
    if (providers.gradleProperty("benchStrict").isPresent) {
        tolerancePercent = 0.0
        channelTolerance = 0
    }
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
