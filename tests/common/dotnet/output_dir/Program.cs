using Altom.AltWalker;
namespace output_dir {
	public class Program {
		public static void Main (string[] args) {
			ExecutorService service = new ExecutorService();
			service.RegisterModel<ModelName>();
			service.Run(args);
		}
	}
}
