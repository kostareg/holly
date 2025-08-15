import { useState } from "react";

import Websocket from "@/components/common/websocket";
import type { TrainingState } from "@/routes/training/training-state";

export const Training = () => {
	const [state, setState] = useState<TrainingState | null>(null);

	return (
		<>
			<Websocket setState={setState} />
			{state?.some}
		</>
	);
};

export default Training;
