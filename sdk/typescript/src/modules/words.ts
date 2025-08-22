import * as WordsType from "../types/words";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class WordsController extends BaseController {

    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** GET /words/ */
    async list(config?: RequestConfig<WordsType.WordsListRequestParams>
    ): Promise<AxiosResponse<WordsType.WordsListResponseData>> {
        return await this.axiosGet(`/words/`, config);
    }
    
    /** POST /words/ */
    async create(data: WordsType.WordsCreateRequestData, config?: RequestConfig<WordsType.WordsCreateRequestParams>
    ): Promise<AxiosResponse<WordsType.WordsCreateResponseData>> {
        return await this.axiosPost(`/words/`, data, config);
    }
    
    /** GET /words/{uuid}/ */
    async retrieve(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<WordsType.WordsRetrieveResponseData>> {
        return await this.axiosGet(`/words/${uuid}/`, config);
    }
    
    /** PUT /words/{uuid}/ */
    async update(uuid: string, data: WordsType.WordsUpdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<WordsType.WordsUpdateResponseData>> {
        return await this.axiosPut(`/words/${uuid}/`, data, config);
    }
    
    /** PATCH /words/{uuid}/ */
    async partialUpdate(uuid: string, data: WordsType.WordsPartialupdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<WordsType.WordsPartialupdateResponseData>> {
        return await this.axiosPatch(`/words/${uuid}/`, data, config);
    }
    
    /** DELETE /words/{uuid}/ */
    async delete(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/words/${uuid}/`, config);
    }
    
}