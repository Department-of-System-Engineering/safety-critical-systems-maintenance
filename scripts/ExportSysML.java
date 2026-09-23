import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import org.omg.sysml.interactive.SysMLInteractive;

/** Parse, validate and export a native model using the SysML v2 Pilot Implementation. */
public class ExportSysML {
    public static void main(String[] args) throws Exception {
        if (args.length != 4) {
            throw new IllegalArgumentException("Usage: ExportSysML libraryDirectory source.sysml packageName output.json");
        }
        var engine = SysMLInteractive.getInstance();
        engine.loadLibrary(args[0]);
        var result = engine.process(Files.readString(Path.of(args[1]), StandardCharsets.UTF_8));
        System.out.println(result.toString());
        if (result.hasErrors()) {
            throw new IllegalArgumentException("Native SysML validation failed");
        }
        String exported = engine.export(args[2], Collections.emptyList()).toString();
        if (exported.startsWith("ERROR:")) {
            throw new IllegalArgumentException(exported);
        }
        Files.writeString(Path.of(args[3]), exported, StandardCharsets.UTF_8);
        System.out.println("Native SysML validation succeeded; exported " + args[3]);
    }
}
